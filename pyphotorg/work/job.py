import os
import common
import organize
import deduplicate

def job(progress_callback=None):
    dry_run_mode = common.is_envvar_true("DRY_RUN_MODE")
    if dry_run_mode:
        print("******* DRY-RUN MODE ENABLED *******")

    organize_enabled = common.is_envvar_true("ENABLE_ORGANIZE")
    deduplicate_enabled = common.is_envvar_true("ENABLE_DEDUPLICATE")
    enabled_operations = organize_enabled + deduplicate_enabled
    operation_index = 0

    def report_operation_progress(progress, message):
        if progress_callback is not None:
            operation_start = operation_index / enabled_operations
            operation_end = (operation_index + 1) / enabled_operations
            progress_callback(
                round((operation_start + progress * (operation_end - operation_start)) * 100),
                message,
            )

    if organize_enabled:
        print("- Launching organize job ...")
        report_operation_progress(0, "Organizing photos and videos")
        organize.organize1(
            path_couples=common.load_org_path_couples1(),
            timestamp_tags=common.load_envvar_comma_list("ORG_TIMESTAMP_TAGS"),
            storage_path_pattern=os.getenv("ORG_STORAGE_PATH_PATTERN"),
            dry_run_mode=dry_run_mode,
            progress_callback=report_operation_progress,
        )
        operation_index += 1

    if deduplicate_enabled:
        print("- Launching deduplicate job ...")
        report_operation_progress(0, "Deduplicating files")
        deduplicate.deduplicate(
            dedup_dir_path=os.getenv("DEDUP_STORAGE_PATH"),
            backup_dir_path=os.getenv("DEDUP_BACKUP_PATH"),
            dir_order_list=common.load_envvars_list("DEDUP_DIR_ORDER"),
            dir_path_filter=os.getenv("DEDUP_DIR_PATH_FILTER"),
            dry_run_mode=dry_run_mode,
            progress_callback=report_operation_progress,
        )
        operation_index += 1

    if progress_callback is not None:
        progress_callback(100, "Job complete")
