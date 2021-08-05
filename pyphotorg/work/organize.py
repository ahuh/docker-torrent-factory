import common
import subprocess

def organize1(path_couples: list[dict], timestamp_tags: list[str], storage_path_pattern: str, dry_run_mode: bool = False):
    """Move photos and videos from 'incoming' path list, and organize them into the corresponding 'storage' path list
    - The program ExifTool is used to extract metadata from files, and organize dir structure and filenames (with suffix generation to prevent overwrite)
    """
    for path_couple in path_couples:
        incoming_path = path_couple["incoming"]
        storage_path = path_couple["storage"]

        if (incoming_path == storage_path):
            print("Organizing photos and videos in '{}' ...".format(storage_path))
            execute_exiftool_cmd2(
                path=storage_path,
                timestamp_tags=timestamp_tags,
                storage_path_pattern=storage_path_pattern,
                dry_run_mode=dry_run_mode
            )
            print("... Organize operation done !")
        else:
            print("Moving photos and videos from '{}' and organizing them into '{}' ...".format(incoming_path, storage_path))
            execute_exiftool_cmd1(
                incoming_path=incoming_path,
                storage_path=storage_path,
                timestamp_tags=timestamp_tags,
                storage_path_pattern=storage_path_pattern,
                dry_run_mode=dry_run_mode
            )
            print("... Move / Organize operation done !")

def organize2(path_list: list[str], timestamp_tags: list[str], storage_path_pattern: str, dry_run_mode: bool = False):
    """Organize photos and videos in path list
    """
    organize1(
        path_couples=common.load_org_path_couples2(path_list=path_list),
        timestamp_tags=timestamp_tags,
        storage_path_pattern=storage_path_pattern,
        dry_run_mode=dry_run_mode
    )

def execute_exiftool_cmd1(incoming_path: str, storage_path: str, timestamp_tags: list[str], storage_path_pattern: str, dry_run_mode: bool = False):
    """Execute ExifTool command in shell for move and organize operations
    - Move files from 'incoming_path' and organize into 'storage_path' (recursively)
    - The ET execution mode 'FileName' is used for move/organize ('TestName' is used instead in dry-run mode)
    - The 'timestamp_tags' corresponds to the metadata to use in reverse order of priority for path / filename insertion. See documentation here: https://exiftool.org/filename.html#ex12
    - The 'storage_path_pattern' parameter uses replacement tokens. See documentation here: https://exiftool.org/filename.html#codes
    - In dry-run mode, no file is processed: operations are only displayed in output
    """
    # Example of generated command:
    # exiftool -r -d '/storage/Photos/dirB/%Y/%Y-%m/%Y%m%d_%H%M%S%%-3c.%%e' '-FileName<FileModifyDate' '-FileName<CreationDate' '-FileName<CreateDate' '-FileName<DateTimeOriginal' '/sync/dirA'

    et_exec_mode = "FileName"
    et_verbose_mode = " -v0"
    et_message_header = ""
    if (dry_run_mode):
        et_exec_mode = "TestName"
        et_verbose_mode = ""
        et_message_header = "[DRY-RUN] "

    cmd = "exiftool -r{} -d '{}/{}'".format(et_verbose_mode, storage_path, storage_path_pattern)
    for timestamp_tag in timestamp_tags:
        cmd += " '-{}<{}'".format(et_exec_mode, timestamp_tag)
    cmd += " '{}'".format(incoming_path)

    print("Execution of ExifTool command:")
    print("> {}".format(cmd))

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stderr:
        common.print_err("* {}ExifTool ERROR: {}".format(et_message_header, stderr.decode("utf-8")))
    if stdout:
        print("* {}ExifTool output: {}".format(et_message_header, stdout.decode("utf-8")))

def execute_exiftool_cmd2(path: str, timestamp_tags: list[str], storage_path_pattern: str, dry_run_mode: bool = False):
    """Execute ExifTool command in shell for move and organize operations
    - Organize files in 'path' (recursively)
    """
    execute_exiftool_cmd1(
        incoming_path=path, 
        storage_path=path,
        timestamp_tags=timestamp_tags,
        storage_path_pattern=storage_path_pattern,
        dry_run_mode=dry_run_mode
    )