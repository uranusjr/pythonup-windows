extern crate pythonup;

use pythonup::{pythons, run};

fn main() {
    run::python(pythons::find_best_using);
}
