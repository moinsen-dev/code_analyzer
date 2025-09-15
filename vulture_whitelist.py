# Vulture whitelist file to ignore false positives

# Signal handler parameters - used in function signature
sig
frame

# CLI functions that may be used by subcommands or future features
init
watch
unused

# AI module variables and methods
analyze_file
line_start
line_end
related_files
project_structure
dependencies
enable_ai_suggestions
max_file_size
cache_results
cache_ttl

# Duplicate detection
CloneType
EXACT
RENAMED
MODIFIED
SEMANTIC
calculate_similarity
_cleanup_expired_cache
_detect_duplicate_code

# Config module
get_language_config
get_analysis_thresholds
get_output_config
version
max_line_length
complexity_threshold

# Watcher module
on_modified
on_created
on_deleted
_last_analysis