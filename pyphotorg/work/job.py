import os
import common
import organize
import deduplicate

def job():
    dry_run_mode = common.is_envvar_true("DRY_RUN_MODE")
    if dry_run_mode:
        print("******* DRY-RUN MODE ENABLED *******")
    
    if common.is_envvar_true("ENABLE_ORGANIZE"):
        print("- Launching organize job ...")
        organize.organize1(
            path_couples=common.load_org_path_couples1(),
            timestamp_tags=common.load_envvar_comma_list("ORG_TIMESTAMP_TAGS"),
            storage_path_pattern=os.getenv("ORG_STORAGE_PATH_PATTERN"),
            dry_run_mode=dry_run_mode
        )

    if common.is_envvar_true("ENABLE_DEDUPLICATE"):
        print("- Launching deduplicate job ...")
        deduplicate.deduplicate(
            dedup_dir_path=os.getenv("DEDUP_STORAGE_PATH"),
            backup_dir_path=os.getenv("DEDUP_BACKUP_PATH"),
            dir_order_list=common.load_envvars_list("DEDUP_DIR_ORDER"),
            dry_run_mode=dry_run_mode
        )
