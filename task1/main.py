import argparse
import datetime
import json
import os
import tarfile
import shutil

from io import BytesIO


class VirtualFileSystem:
    def __init__(self, tar_path):
        self.tar_path = tar_path
        self.current_dir = "/"

    def _open_tar(self, mode):
        return tarfile.open(self.tar_path, mode)

    def _get_path(self, path):
        if path.startswith("/"):
            return path
        return os.path.normpath(os.path.join(self.current_dir, path))

    def ls(self, path):
        full_path = self._get_path(path)
        with self._open_tar("r") as tar:
            for member in tar:
                if member.name.startswith(full_path):
                    yield member.name

    def cd(self, path):
        full_path = self._get_path(path)
        with self._open_tar("r") as tar:
            if any(member.name == full_path for member in tar):
                self.current_dir = full_path
            else:
                raise FileNotFoundError(f"No such directory: {full_path}")

    def mkdir(self, path):
        full_path = self._get_path(path)
        with self._open_tar("a") as tar:
            tarinfo = tarfile.TarInfo(full_path)
            tarinfo.type = tarfile.DIRTYPE
            tarinfo.mtime = datetime.datetime.now().timestamp()
            tar.addfile(tarinfo)

    def mv(self, src, dst):
        full_src = self._get_path(src)
        full_dst = self._get_path(dst)
        with self._open_tar("r") as tar:
            with self._open_tar("w") as new_tar:
                for member in tar:
                    if member.name == full_src:
                        member.name = full_dst
                    new_tar.addfile(member, tar.extractfile(member))
        shutil.move(self.tar_path + ".tmp", self.tar_path)

    def rmdir(self, path):
        full_path = self._get_path(path)
        with self._open_tar("r") as tar:
            with self._open_tar("w") as new_tar:
                for member in tar:
                    if not member.name.startswith(full_path):
                        new_tar.addfile(member, tar.extractfile(member))
        shutil.move(self.tar_path + ".tmp", self.tar_path)


class ShellEmulator:
    def __init__(self, username, hostname, fs_path, log_path, start_script_path):
        self.username = username
        self.hostname = hostname
        self.fs = VirtualFileSystem(fs_path)
        self.log_path = log_path
        self.start_script_path = start_script_path
        self.log = []

    def _log_action(self, command, args):
        self.log.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "user": self.username,
            "command": command,
            "args": args
        })

    def _run_command(self, command, args):
        if command == "ls":
            for file in self.fs.ls(args[0] if args else "."):
                print(file)
        elif command == "cd":
            self.fs.cd(args[0])
        elif command == "mkdir":
            self.fs.mkdir(args[0])
        elif command == "mv":
            self.fs.mv(args[0], args[1])
        elif command == "rmdir":
            self.fs.rmdir(args[0])
        elif command == "exit":
            return False
        else:
            print(f"Command not found: {command}")
        return True

    def run(self):
        if self.start_script_path:
            with open(self.start_script_path, "r") as f:
                for line in f:
                    command, *args = line.strip().split()
                    self._log_action(command, args)
                    self._run_command(command, args)

        while True:
            try:
                command_line = input(f"{self.username}@{self.hostname}:{self.fs.current_dir}$ ")
                command, *args = command_line.strip().split()
                self._log_action(command, args)
                if not self._run_command(command, args):
                    break
            except Exception as e:
                print(e)

        with open(self.log_path, "w") as f:
            json.dump(self.log, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--hostname", required=True, help="Hostname")
    parser.add_argument("--fs", required=True, help="Path to virtual filesystem tar archive")
    parser.add_argument("--log", required=True, help="Path to log file")
    parser.add_argument("--start_script", help="Path to start script")
    args = parser.parse_args()

    emulator = ShellEmulator(args.username, args.hostname, args.fs, args.log, args.start_script)
    emulator.run()