import rustpython_ast as rust_ast
import ast

class_registry = {}

src = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def match_point(p):
    match p:
        case Point(x, y):
            return f"Point at ({x}, {y})"
        case _:
            return "Not a Point"

point = Point(3, 4)
print(match_point(point))  # Output: Point at (3, 4)
"""

res = rust_ast.parse_wrap(src)


class _AST:
    pass


def traverse(obj, level=0):
    indent = "  " * level  # Indentation for visual clarity
    if isinstance(obj, (list, tuple)):
        # If the object is a list or tuple, iterate through its items
        for index, item in enumerate(obj):
            print(f"{indent}Index {index}:")
            traverse(item, level + 1)
    elif hasattr(obj, '_fields'):
        # If the object has a _fields attribute, traverse its attributes
        print(f"{indent}Object of type {type(obj).__name__}:")
        for attr in dir(obj):
            if attr.startswith('_'):
                continue  # Skip private attributes
            value = getattr(obj, attr)
            print(f"{indent}  Attribute '{attr}':")
            traverse(value, level + 1)
    else:
        # For other types, just print the value
        print(f"{indent}Value: {obj}")


def transform_to_ast(obj):
    if isinstance(obj, list):
        # If the object is a list, transform each element
        return [transform_to_ast(item) for item in obj]
    elif isinstance(obj, tuple):
        # If the object is a tuple, transform each element
        return tuple(transform_to_ast(item) for item in obj)
    elif hasattr(obj, '_fields'):
        # If the object has a _fields attribute, get the corresponding AST class
        class_name = obj.__class__.__name__
        if class_name.startswith("_"):
            class_name = class_name[1:]
        ast_class = getattr(ast, class_name, None)
        if ast_class is None:
            # Create a new class dynamically if it doesn't exist
            if class_name not in class_registry:
                # print(f"No corresponding AST class for {class_name}, creating one")
                new_class = type(class_name, (_AST,), {field: None for field in obj._fields})
                class_registry[class_name] = new_class
            else:
                new_class = class_registry[class_name]
            new_class_instance = new_class()
            for field in obj._fields:
                setattr(new_class_instance, field, transform_to_ast(getattr(obj, field)))
            return new_class_instance
        else:
            fields = {field: transform_to_ast(getattr(obj, field)) for field in obj._fields}
            return ast_class(**fields) if obj._fields else ast_class()

    else:
        # If the object does not match any criteria, return it as is
        return obj


# Function to pretty-print the AST
def pretty_print_ast(node, level=0):
    indent = ' ' * (level * 4)  # 4 spaces for each level of indentation
    if isinstance(node, list):
        for item in node:
            pretty_print_ast(item, level)
    elif isinstance(node, tuple):
        print(indent + '(')
        for item in node:
            pretty_print_ast(item, level + 1)
        print(indent + ')')
    elif isinstance(node, ast.AST):
        print(f"{indent}{node.__class__.__name__}:")
        for field, value in ast.iter_fields(node):
            print(f"{indent}  {field}: ")
            pretty_print_ast(value, level + 1)
    elif isinstance(node, _AST):
        print(f"{indent}{node.__class__.__name__}:")
        for field in dir(node):
            if not field.startswith('_'):
                print(f"{indent}  {field}: ")
                pretty_print_ast(getattr(node, field), level + 1)
    else:
        print(f"{indent}{node}")


res1 = transform_to_ast(res)
pretty_print_ast(res1)

