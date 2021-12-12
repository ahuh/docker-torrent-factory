import common
import os
import shutil
import time
import duplicates
import pandas as pd

def deduplicate(dedup_dir_path: str, backup_dir_path: str, dir_order_list: list[str] = None, dir_path_filter: str = None, dry_run_mode: bool = False):
    """Deduplicate files in 'dedup_dir_path', and move them in 'backup_dir_path'
    """

    df = build_duplicate_df(
        dedup_dir_path=dedup_dir_path,
        backup_dir_path=backup_dir_path,
        dir_order_list=dir_order_list,
        dir_path_filter=dir_path_filter
    )

    if not df.empty:
        remove_duplicate(
            df=df,
            dedup_dir_path=dedup_dir_path,
            backup_dir_path=backup_dir_path,
            dry_run_mode=dry_run_mode
        )

def build_duplicate_df(dedup_dir_path: str, backup_dir_path: str, dir_order_list: list[str] = None, dir_path_filter: str = None) -> pd.DataFrame:
    """List duplicate files in 'dedup_dir_path', based on filesize (must be the same) and hash (must be the same)
    - Build a dataframe with 'file' column (full path) and 'duplicate' column (True for files marked for removal)
    - Order algorithm applied to keep only best file for each duplicate set: prioritize dirs from 'dir_order_list', then first dirs in alphabetic path order, then filename length (keep shortest)
    - Generate a report in 'backup_dir_path' (unless no duplicate to remove)
    """
    print("Listing all duplicates in '{}' ...".format(dedup_dir_path))

    df = pd.DataFrame(columns=['file', 'hash', 'dirpath', 'filename', 'filename_length', 'order', 'duplicate'])
    with common.IgnoreStdout():
        df = duplicates.list_all_duplicates(dedup_dir_path, fastscan=True)

    if (dir_order_list is None):
            # Default dir order list if none
            dir_order_list = ['/']

    if ((not df.empty) and (dir_path_filter is not None)):
        # Do not process files containing path filter
        df = df[~df['file'].str.contains(dir_path_filter)]

    if df.empty:
        print("... No duplicate to remove !")
    else:
        # Add a dir path column extracted from 'file' column with full path
        df['dirpath'] = df.apply(lambda x: os.path.dirname(x['file']), axis=1)

        # Add a file name column extracted from 'file' column with full path
        df['filename'] = df.apply(lambda x: os.path.basename(x['file']), axis=1)

        # Add a filename length column extracted from 'filename' column
        df['filename_length'] = df.apply(lambda x: len(x['filename']), axis=1)

        # Calculate and add an order column to prioritize files to deduplicate (from lowest to highest value)
        df['order'] = df.apply(lambda x: min([dir_order_list.index(i) if x['file'].lower().startswith(i.lower()) else 9999 for i in dir_order_list]), axis=1)

        # Sort table:
        # 1) By dir priority order (ascending)
        # 2) By dir path (ascending)
        # 3) By filename length (ascending)
        df.sort_values(by=['order', 'dirpath', 'filename_length'], ascending=True, inplace=True)

        # Mark duplicates to remove: we only keep the 1st duplicate for each hash in the sorted table
        df['duplicate'] = df.duplicated(subset=['hash'], keep='first')

        # Generate report
        duplicate_report_path = "{}/duplicate_report_{}.xlsx".format(backup_dir_path, time.strftime("%Y%m%d_%H%M%S"))
        print("Generating duplicate report at path '{}' ...".format(duplicate_report_path))
        df.to_excel(duplicate_report_path)

        print("... Duplicate listing done !")

    return df

def remove_duplicate(df: pd.DataFrame, dedup_dir_path: str, backup_dir_path: str, dry_run_mode: bool = False):
    """Remove duplicate files marked in the input DataFrame 'df'
    - Remove file from df['file'] column (full path) with df['duplicate'}=True (marked for removal)
    - No physical deletion: files are move from 'dedup_dir_path' to 'backup_dir_path', reproducing the same dir structure and file names
    - In dry-run mode, no file is processed: operations are only simulated and displayed in output
    """
    print("Removing duplicates in '{}' ...".format(dedup_dir_path))

    for remove_file_path in df[df['duplicate'] == True]['file'].tolist():
        path_suffix = remove_file_path.replace(dedup_dir_path, "", 1)
        backup_file_path = backup_dir_path + path_suffix
        backup_file_dir = os.path.dirname(backup_file_path)

        if dry_run_mode:
            if not os.path.exists(backup_file_dir):
                print("* [DRY-RUN] Simulate dir creation before move: '{}'".format(backup_file_dir))
            print("* [DRY-RUN] Simulate duplicate file move: '{}' -> '{}'".format(remove_file_path, backup_file_path))
        else:
            print("* Move duplicate file: '{}' -> '{}'".format(remove_file_path, backup_file_path))
            if not os.path.exists(backup_file_dir):
                os.makedirs(backup_file_dir)
            shutil.move(remove_file_path, backup_file_path)

    print("... Duplicate files removed !")
