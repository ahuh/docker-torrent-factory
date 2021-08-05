import os
import sys
import argparse
import common
import organize

# ======================================
# Main
def main(argv):

    p = argparse.ArgumentParser(description="Launch organize operation manually on dirs (organize only) or on couples of dirs (move from incoming dirs, organize into storage dirs).")
    p.add_argument('-i', '--incoming-dir-list', required=False, nargs='*', help="List of incoming dir paths, with files to move to storage (if empty: no file move)")
    p.add_argument('-s', '--storage-dir-list', required=False, nargs='*', help="List of storage dir paths, with files to organize (if empty: use default env var)")
    p.add_argument('-t', '--timestamp-tags', required=False, nargs='*', default=common.load_envvar_comma_list("ORG_TIMESTAMP_TAGS"),
        help="List of metadata tags to use in reverse order of priority for path / filename insertion (default value from env var")
    p.add_argument('-p', '--storage-path-pattern', required=False, default=os.getenv("ORG_STORAGE_PATH_PATTERN"),
        help="Storage path pattern to use for directory structure / filename from photo / video dates metadatas (default value from env var")
    p.add_argument('-y', '--dry-run', required=False, action='store_true', help="Dry-run mode (default to False)")

    args = p.parse_args(argv)

    print("=====================================")
    print("Launching manual organize operation with args ...")
    print('- incoming-dir-list={}'.format(args.incoming_dir_list))
    print('- storage-dir-list={}'.format(args.storage_dir_list))
    print('- timestamp-tags={}'.format(args.timestamp_tags))
    print('- storage-path-pattern={}'.format(args.storage_path_pattern))
    print('- dry-run={}'.format(args.dry_run))
    print("=====================================")

    arg_path_couples = {}
    if args.incoming_dir_list and args.storage_dir_list:
        arg_path_couples = common.load_org_path_couples3(
            incoming_list=args.incoming_dir_list,
            storage_list=args.storage_dir_list
        )
    elif args.storage_dir_list:
        arg_path_couples = common.load_org_path_couples2(
            path_list=args.storage_dir_list
        )
    else:
        arg_path_couples = common.load_org_path_couples1()
    
    organize.organize1(
        path_couples=arg_path_couples,
        timestamp_tags=args.timestamp_tags,
        storage_path_pattern=args.storage_path_pattern,
        dry_run_mode=args.dry_run
    )

    print("... Operation ended !")

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])