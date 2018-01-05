extern crate pythonup;

use pythonup::{pythons, run};

fn main() {
    run::pymod_and_link(pythons::find_best_using);
}
