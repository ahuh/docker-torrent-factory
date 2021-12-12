import sys
import argparse
import common
import deduplicate

# ======================================
# Main
def main(argv):

    p = argparse.ArgumentParser(description="Launch deduplicate operation manually on a dir.")
    p.add_argument('-d', '--dedup-dir-path', required=True, help="Path to dir to deduplicate")
    p.add_argument('-b', '--backup-dir-path', required=True, help="Path to backup dir")
    p.add_argument('-o', '--dir-order-list', required=False, nargs='*', default=common.load_envvars_list("DEDUP_DIR_ORDER"),
        help="List of ordered-by-priority dirs paths for deduplicate (default value from env var)")
    p.add_argument('-f', '--dir-path-filter', required=False, default=common.load_envvars_list("DEDUP_DIR_PATH_FILTER"),
        help="Dir path filter to exclude from operation (default value from env var)")
    p.add_argument('-y', '--dry-run', required=False, action='store_true', help="Dry-run mode (default to False)")

    args = p.parse_args(argv)

    print("=====================================")
    print("Launching manual deduplicate operation with args ...")
    print('- dedup-dir-path={}'.format(args.dedup_dir_path))
    print('- backup-dir-path={}'.format(args.backup_dir_path))
    print('- dir-order-list={}'.format(args.dir_order_list))
    print('- dir-path-filter={}'.format(args.dir_path_filter))
    print('- dry-run={}'.format(args.dry_run))
    print("=====================================")

    deduplicate.deduplicate(
        dedup_dir_path=args.dedup_dir_path,
        backup_dir_path=args.backup_dir_path,
        dir_order_list=args.dir_order_list,
        dir_path_filter=args.dir_path_filter,
        dry_run_mode=args.dry_run
    )

    print("... Operation ended !")

if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])