#pragma once
#include <map>
#include <string>
#include <vector>
class CrawlHashTable;

namespace holo34 {
enum class ability_kind { active, passive, mixed, passive_with_targeting };
struct ability_definition {
    const char *id;
    const char *name;
    int tier;
    int piety_required;
    ability_kind kind;
    bool implemented;
};
struct god_definition {
    const char *id;
    const char *name;
    ability_definition abilities[5];
};
struct god_state {
    int joins = 0;
    int departures = 0;
    std::string mode;
    std::map<std::string, int> resources;
    std::map<std::string, int> cooldown_aut;
    std::map<std::string, int> duration_aut;
};
struct state {
    int schema = 1;
    std::string current;
    int piety = 0;
    std::map<std::string, god_state> per_god;
};
// These operations manage framework data only. Live-game worship, costs,
// wrath and combat hooks are not yet connected.
const god_definition *find_god(const std::string &id);
std::vector<std::string> god_ids();
bool worship(state &s, const std::string &id);
bool renounce(state &s);
bool grant_piety(state &s, int amount);
int rank(const state &s);
void validate(const state &s);
enum class invocation_result { unknown_ability, wrong_god, locked, passive, not_implemented };
invocation_result invoke(state &s, const std::string &ability_id);
// Versioned property adapter; callers can supply player.props when gameplay
// is connected. No native god enum or native piety is changed here.
void save_properties(CrawlHashTable &owner, const state &s);
state load_properties(const CrawlHashTable &owner);
// Returns -1 when not a framework diagnostic command.
int command_line(int argc, char **argv);
}
