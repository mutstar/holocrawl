#pragma once
#include <string>
#include <vector>

// Campaign membership only. Combat benchmark statics are deliberately not
// enabled until their effects have a level-aware persistence implementation.
namespace holo_worship {
std::vector<std::string> gods();
std::string current();
std::string display_name();
bool active();
int history_count();
int rank();
bool join(const std::string &god, bool announce=true);
bool renounce(bool announce=true);
bool altar_menu(); // false: continue the original altar's native conversion.
void religion_menu();
void show_info(const std::string &god);
void validate_save();
bool test_requested();
int run_tests();
}
