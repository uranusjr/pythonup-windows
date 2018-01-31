use std::env::current_exe;
use std::fs::File;
use std::io::{self, Read};
use std::path::PathBuf;
use std::vec::IntoIter;

#[derive(Debug)]
pub struct Command {
    exe: Option<PathBuf>,
    args: Vec<String>,
}

impl Command {
    pub fn new() -> Self {
        Command { exe: None, args: vec![] }
    }

    pub fn arg(&mut self, arg: String) {
        match self.exe {
            Some(_) => self.args.push(arg),
            None => self.exe = Some(PathBuf::from(arg)),
        }
    }

    pub fn exe(&self) -> Option<&PathBuf> {
        self.exe.as_ref()
    }

    pub fn args(&self) -> &Vec<String> {
        &self.args
    }
}

pub struct Commands {
    iter: IntoIter<Result<u8, io::Error>>,
    done: bool,
}

// Helper to push a byte array as argument into command.
macro_rules! push_arg {
    ( $command:expr, $bytes:expr ) => {
        match String::from_utf8($bytes) {
            Ok(arg) => { $command.arg(arg); },
            Err(e) => {
                eprintln!("bad shim: {}", e);
                return None;
            },
        }
    };
}

impl Commands {
    pub fn from(bytes: Vec<Result<u8, io::Error>>) -> Self {
        Commands { iter: bytes.into_iter(), done: false }
    }

    pub fn from_current_exe() -> Result<Self, String> {
        let exe = current_exe().map_err(|e| e.to_string())?;
        let file = File::open(&exe).map_err(|e| e.to_string())?;

        let mut bytes: Vec<_> = io::BufReader::new(file).bytes().collect();
        bytes.reverse();

        Ok(Self::from(bytes))
    }

    fn read_next_command(&mut self) -> Option<Command> {
        let mut command = Command::new();
        let mut bytes = vec![];
        while let Some(result) = self.iter.next() { match result {
            Ok(byte) => match byte {
                10 => { // Line feed.
                    if !bytes.is_empty() {
                        push_arg!(command, bytes);
                    }
                    return match command.exe() {
                        Some(_) => Some(command),
                        None => None,
                    };
                },
                0 => {  // Null.
                    push_arg!(command, bytes);
                    bytes = vec![];
                },
                _ => { bytes.push(byte); },
            },
            Err(e) => {
                eprintln!("shim read failure: {}", e);
                return None;
            },
        }}
        None
    }
}

impl Iterator for Commands {
    type Item = Command;

    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }
        match self.read_next_command() {
            r @ Some(_) => r,
            None => { self.done = true; None },
        }
    }
}


#[cfg(test)]
mod command_test {
    use std::path::PathBuf;
    use super::Command;

    #[test]
    fn new() {
        let command = Command::new();
        assert_eq!(command.exe(), None);
        assert_eq!(command.args(), &Vec::<String>::new());
    }

    #[test]
    fn push_exe() {
        let mut command = Command::new();
        command.arg(String::from("C:\\python.exe"));
        assert_eq!(command.exe(), Some(&PathBuf::from("C:\\python.exe")));
        assert_eq!(command.args(), &Vec::<String>::new());
    }

    #[test]
    fn push_exe_arg() {
        let mut command = Command::new();
        command.arg(String::from("C:\\python.exe"));
        command.arg(String::from("-OO"));
        command.arg(String::from("-c"));
        command.arg(String::from("import sys; print(sys.executable)"));
        assert_eq!(command.exe(), Some(&PathBuf::from("C:\\python.exe")));
        assert_eq!(command.args(), &vec![
            String::from("-OO"),
            String::from("-c"),
            String::from("import sys; print(sys.executable)"),
        ]);
    }
}


#[cfg(test)]
mod commands_test {
    use std::path::PathBuf;
    use super::Commands;

    #[test]
    fn consume_all() {
        let mut commands = Commands::from("\
            C:\\python.exe\n\
            C:\\python.exe\0--version\n\
            C:\\python.exe\0-OO\0-c\0import sys; print(sys.executable)\n\
        ".bytes().map(|b| Ok(b)).collect());

        let command = commands.next().unwrap();
        assert_eq!(command.exe(), Some(&PathBuf::from("C:\\python.exe")));
        assert_eq!(command.args(), &Vec::<String>::new());

        let command = commands.next().unwrap();
        assert_eq!(command.exe(), Some(&PathBuf::from("C:\\python.exe")));
        assert_eq!(command.args(), &vec![String::from("--version")]);

        let command = commands.next().unwrap();
        assert_eq!(command.exe(), Some(&PathBuf::from("C:\\python.exe")));
        assert_eq!(command.args(), &vec![
            String::from("-OO"),
            String::from("-c"),
            String::from("import sys; print(sys.executable)"),
        ]);

        assert_eq!(commands.next().is_none(), true);
    }

    #[test]
    fn avoid_garbage() {
        let mut commands = Commands::from(
            "C:\\python.exe\n\n12345".bytes().map(|b| Ok(b)).collect(),
        );

        let command = commands.next().unwrap();
        assert_eq!(command.exe(), Some(&PathBuf::from("C:\\python.exe")));
        assert_eq!(command.args(), &Vec::<String>::new());

        assert_eq!(commands.next().is_none(), true);
        assert_eq!(commands.next().is_none(), true);
        assert_eq!(commands.next().is_none(), true);
    }
}
