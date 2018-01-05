extern crate pythonup;

use pythonup::procs::{setup, run_and_end};
use pythonup::pythons::find_of_snafu;
use pythonup::run::print_and_abort;

/// Entry point of the pythonup.exe shim executable.
fn main() {
    let python = find_of_snafu().unwrap_or_else(print_and_abort);
    setup().unwrap_or_else(print_and_abort);
    run_and_end(&python, &vec!["-m", "pythonup"], true);
}
