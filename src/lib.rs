mod py_ast;
#[cfg(feature = "wrapper")]
pub mod wrapper;
#[cfg(feature = "wrapper")]
pub use wrapper::{ToPyWrapper, located, ranged};
#[cfg(not(feature = "wrapper"))]
pub use py_ast::{init, PyNode, ToPyAst};


use pyo3::prelude::*;
use rustpython_parser::ast::{source_code::LinearLocator, Fold};

#[pyfunction]
#[cfg(not(feature = "wrapper"))]
#[pyo3(signature = (source, filename="<unknown>", *, type_comments=false, locate=true))]
pub fn parse<'py>(
    source: &str,
    filename: &str,
    type_comments: bool,
    locate: bool,
    py: Python<'py>,
) -> PyResult<&'py PyAny> {
    if type_comments {
        todo!("'type_comments' is not implemented yet");
    }
    let parsed = rustpython_parser::parse(source, rustpython_parser::Mode::Module, filename)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PySyntaxError, _>(e.to_string()))?;
    if locate {
        let parsed = LinearLocator::new(source).fold(parsed).unwrap();
        parsed.module().unwrap().to_py_ast(py)
    } else {
        parsed.module().unwrap().to_py_ast(py)
    }
}

#[pyfunction]
#[cfg(feature = "wrapper")]
#[pyo3(signature = (source, filename="<unknown>", *, type_comments=false, locate=true))]
pub fn parse_wrap<'py>(
    source: &str,
    filename: &str,
    type_comments: bool,
    locate: bool,
    py: Python,
) -> PyResult<PyObject> {
    if type_comments {
        todo!("'type_comments' is not implemented yet");
    }
    let parsed = rustpython_parser::parse(source, rustpython_parser::Mode::Module, filename)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PySyntaxError, _>(e.to_string()))?;
    if locate {
        let parsed = LinearLocator::new(source).fold(parsed).unwrap();
        let parsed = Box::leak(Box::new(parsed));
        parsed.to_py_wrapper(py)
    } else {
        let parsed = Box::leak(Box::new(parsed));
        parsed.to_py_wrapper(py)
    }
}


#[pymodule]
fn rustpython_ast(py: Python, m: &PyModule) -> PyResult<()> {

    #[cfg(not(feature = "wrapper"))] {
        py_ast::init(py)?;
        m.add_function(wrap_pyfunction!(parse, m)?)?;
    }

    #[cfg(feature = "wrapper")]
    {
        let ast = PyModule::new(py, "located")?;
        wrapper::located::add_to_module(py, ast)?;
        m.add_submodule(ast)?;

        let ast = PyModule::new(py, "ranged")?;
        wrapper::ranged::add_to_module(py, ast)?;
        m.add_submodule(ast)?;

        m.add_function(wrap_pyfunction!(parse_wrap, m)?)?;
    }
    Ok(())
}
