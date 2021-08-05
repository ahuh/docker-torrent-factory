import os
import sys
import traceback

class IgnoreStdout(object):
    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self

    def __exit__(self, type, value, traceback):
        sys.stdout = self.stdout
        #if type is not None:
            # Do normal exception handling
    
    def write(self, x): pass

def print_err(message: str):
    """Print message to error output
    """
    print(message, file=sys.stderr)

def load_envvars_list(envvar_prefix: str) -> list[str]:
    """Load a list of environment variables as a list of string
    * A prefix is used to retrieve variables, and values are ordered by ascending suffix
    * Example env vars: EGVAR_01=toto ; EGVAR_02=titi
    * Resulting output for prefix EGVAR: ["toto", "titi"]
    """
    output = []
    for key, value in sorted(os.environ.items()):
        if (key.startswith(envvar_prefix)):
            output.append(value)
    return output

def load_org_path_couples1() -> list[dict]:
    """Load the ORG_INCOMING_PATH_* and ORG_STORAGE_PATH_* env vars as an array of dictionary
    - Keys: "incoming" and "storage"
    """
    return load_org_path_couples3(
        incoming_list=load_envvars_list("ORG_INCOMING_PATH"),
        storage_list=load_envvars_list("ORG_STORAGE_PATH")
    )

def load_org_path_couples2(path_list: list[str]) -> list[dict]:
    """Load path list (same list for incoming and storage) as an array of dictionary
    - Keys: "incoming" and "storage"
    """
    return load_org_path_couples3(
        incoming_list=path_list,
        storage_list=path_list
    )

def load_org_path_couples3(incoming_list: list[str], storage_list: list[str]) -> list[dict]:
    """Load incoming and storage path lists as an array of dictionary
    - Keys: "incoming" and "storage"
    """
    output = []
    for i in range(len(incoming_list)):
        row = {
            "incoming": incoming_list[i],
            "storage": storage_list[i]
        }
        output.append(row)
    return output

def load_envvar_comma_list(envvar: str) -> list[str]:
    """Load an env var as an array by splitting value with ","
    """
    output = []
    tags = os.getenv(envvar)
    if (tags != None):
        output = tags.split(",")
    return output

def is_envvar_true(envvar: str) -> bool:
    """Return True if the env var equals 'true', False otherwise
    """
    dryrun_mode = os.getenv(envvar)
    return (dryrun_mode != None and dryrun_mode.lower() == "true")
