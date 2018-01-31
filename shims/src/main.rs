mod cmds;
mod procs;

use std::process::{abort, exit};
use self::cmds::Commands;
use self::procs::{setup, run};

macro_rules! run_or_exit {
    ( $cmd:expr, $own_args:expr ) => {
        match run($cmd.exe().unwrap(), $cmd.args(), $own_args) {
            Ok(code) => if code != 0 { exit(code) },
            Err(e) => { eprintln!("{}", e); abort(); },
        }
    };
}

fn main() {
    let mut cmds = Commands::from_current_exe().unwrap_or_else(|e| {
        eprintln!("{}", e);
        abort();
    });

    setup().unwrap_or_else(|e| { eprintln!("{}", e); abort(); });
    match cmds.next() {
        Some(cmd) => run_or_exit!(cmd, true),
        None => { abort(); },
    };
    for cmd in cmds {
        run_or_exit!(cmd, false);
    }
}
