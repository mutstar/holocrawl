#include "AppHdr.h"
#include "holo34-framework.h"
#include "holo34-visibility.h"
#include "store.h"
#include "tags.h"
#include <algorithm>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <set>
#include <stdexcept>

namespace holo34 {
namespace {
#include "holo34-catalog.inc"
const char *property_key = "holocrawl0341";
void require(bool condition, const char *message)
{
    if (!condition) throw std::runtime_error(message);
}
const CrawlStoreValue &field(const CrawlHashTable &t, const char *key, store_val_type type)
{
    require(t.exists(key), "Missing HoloCrawl framework save field");
    const auto &v = t.at(key);
    require(v.get_type() == type, "Wrong HoloCrawl framework save field type");
    return v;
}
CrawlHashTable numbers(const std::map<std::string, int> &values)
{
    CrawlHashTable t;
    for (const auto &v : values) t[v.first] = v.second;
    return t;
}
std::map<std::string, int> read_numbers(const CrawlHashTable &t)
{
    require(t.size() <= 128, "Too many god state values");
    std::map<std::string, int> result;
    for (const auto &v : t) {
        require(!v.first.empty() && v.first.size() <= 64, "Invalid god state key");
        require(v.second.get_type() == SV_INT, "Wrong god state value type");
        require(v.second.get_int() >= 0, "Negative god state value");
        result[v.first] = v.second.get_int();
    }
    return result;
}
std::vector<unsigned char> encode(const state &s)
{
    CrawlHashTable owner;
    save_properties(owner, s);
    std::vector<unsigned char> bytes;
    writer out(&bytes);
    owner.write(out);
    require(out.succeeded(), "Framework property serialization failed");
    return bytes;
}
state decode(const std::vector<unsigned char> &bytes)
{
    require(!bytes.empty() && bytes.size() <= 1024 * 1024, "Invalid framework fixture length");
    reader in(bytes, TAG_MINOR_VERSION);
    CrawlHashTable owner;
    owner.read(in);
    require(!in.valid(), "Trailing framework fixture bytes");
    return load_properties(owner);
}
state fixture()
{
    state s;
    for (const auto &id : god_ids()) {
        require(worship(s, id), "Fixture worship failed");
        grant_piety(s, 75);
    }
    require(worship(s, "suisei"), "Fixture final worship failed");
    grant_piety(s, 100);
    s.per_god["suisei"].resources["stars"] = 3;
    s.per_god["suisei"].cooldown_aut["tier3"] = 20;
    s.per_god["suisei"].duration_aut["reward"] = 30;
    s.per_god["suisei"].mode = "marked";
    return s;
}
int self_test()
{
    int checks = 0;
    auto check = [&](bool ok, const char *msg) { ++checks; require(ok, msg); };
    check(god_ids().size() == 22, "Expected 22 gods");
    std::set<std::string> abilities;
    state s;
    CrawlHashTable empty;
    check(load_properties(empty).current.empty() && empty.empty(), "Read changed empty properties");
    check(!worship(s, "unknown") && s.per_god.empty(), "Unknown worship mutated state");
    for (const auto &id : god_ids()) {
        const auto *g = find_god(id);
        check(g != nullptr, "Missing god definition");
        check(worship(s, id), "Worship transition failed");
        const auto before = encode(s);
        check(!worship(s, id) && encode(s) == before, "Repeated worship changed state");
        for (const auto &a : g->abilities) {
            check(abilities.insert(a.id).second && !a.implemented, "Duplicate or falsely enabled ability");
            s.piety = a.piety_required - 1;
            check(invoke(s, a.id) == invocation_result::locked, "Locked ability allowed");
            s.piety = a.piety_required;
            const auto snap = encode(s);
            const auto result = invoke(s, a.id);
            check(result == invocation_result::not_implemented || result == invocation_result::passive,
                  "Missing handler reported success");
            check(encode(s) == snap, "Unimplemented ability charged or mutated state");
        }
        grant_piety(s, 1000000);
        check(s.piety == 200 && rank(s) == 5, "Piety upper bound failed");
        grant_piety(s, -1000000);
        check(s.piety == 0 && rank(s) == 0, "Piety lower bound failed");
        s.per_god[id].resources["counter"] = 3;
        s.per_god[id].cooldown_aut["tier3"] = 11;
        s.per_god[id].duration_aut["field"] = 22;
        s.per_god[id].mode = "sample";
        const auto encoded = encode(s);
        check(encode(decode(encoded)) == encoded, "Native property round trip failed");
    }
    const auto active = s.current;
    check(renounce(s), "Renounce failed");
    check(s.current.empty() && s.piety == 0 && s.per_god[active].resources.empty()
          && s.per_god[active].cooldown_aut.empty() && s.per_god[active].duration_aut.empty()
          && s.per_god[active].mode.empty() && s.per_god[active].departures == 1,
          "Renounce leaked transient god data");
    check(s.per_god.size() == 22 && !grant_piety(s, 10), "History or inactive piety failed");
    auto good = fixture();
    check(encode(decode(encode(good))) == encode(good), "Multi-god fixture round trip failed");
    CrawlHashTable owner;
    save_properties(owner, good);
    owner[property_key].get_table()["schema"] = 999;
    bool rejected = false;
    try { load_properties(owner); } catch (const std::runtime_error &) { rejected = true; }
    check(rejected, "Unknown schema accepted");
    save_properties(owner, good);
    owner[property_key].get_table()["current"] = std::string("unknown");
    rejected = false;
    try { load_properties(owner); } catch (const std::runtime_error &) { rejected = true; }
    check(rejected, "Unknown saved god accepted");
    auto invalid = good;
    invalid.piety = 201;
    const auto owner_size = owner.size();
    rejected = false;
    try { save_properties(owner, invalid); } catch (const std::runtime_error &) { rejected = true; }
    check(rejected && owner.size() == owner_size, "Invalid state accepted");
    std::printf("{\"status\":\"passed\",\"gods\":22,\"slots\":110,\"checks\":%d,\"combatHandlersEnabled\":0,\"liveGameHooksConnected\":false}\n", checks);
    return 0;
}
}
const god_definition *find_god(const std::string &id)
{
    for (const auto &g : registry) if (id == g.id) return &g;
    return nullptr;
}
std::vector<std::string> god_ids()
{
    std::vector<std::string> ids;
    for (const auto &g : registry) ids.push_back(g.id);
    return ids;
}
void validate(const state &s)
{
    require(s.schema == 1, "Unsupported HoloCrawl framework schema");
    require(s.piety >= 0 && s.piety <= 200, "Invalid framework piety");
    require(!s.current.empty() || s.piety == 0, "Piety without a Holo god");
    require(s.current.empty() || find_god(s.current), "Unknown current Holo god");
    require(s.current.empty() || s.per_god.count(s.current), "Missing current god state");
    for (const auto &g : s.per_god) {
        require(find_god(g.first) != nullptr, "Unknown god in framework save");
        require(g.second.joins >= 1 && g.second.departures >= 0
                && g.second.departures <= g.second.joins, "Invalid god history counters");
        require(g.second.mode.size() <= 64, "God mode too long");
        for (const auto *values : {&g.second.resources, &g.second.cooldown_aut, &g.second.duration_aut}) {
            require(values->size() <= 128, "Too many god state values");
            for (const auto &v : *values) require(!v.first.empty() && v.first.size() <= 64 && v.second >= 0,
                                                 "Invalid god state value");
        }
    }
}
bool renounce(state &s)
{
    validate(s);
    if (s.current.empty()) return false;
    auto &old = s.per_god.at(s.current);
    ++old.departures;
    old.mode.clear(); old.resources.clear(); old.cooldown_aut.clear(); old.duration_aut.clear();
    s.current.clear(); s.piety = 0;
    return true;
}
bool worship(state &s, const std::string &id)
{
    validate(s);
    if (!find_god(id) || s.current == id) return false;
    renounce(s);
    s.current = id; s.piety = 0;
    ++s.per_god[id].joins;
    return true;
}
bool grant_piety(state &s, int amount)
{
    validate(s);
    if (s.current.empty()) return false;
    s.piety = static_cast<int>(std::max<int64_t>(0, std::min<int64_t>(200, int64_t(s.piety) + amount)));
    return true;
}
int rank(const state &s)
{
    validate(s);
    const auto *g = find_god(s.current);
    int result = 0;
    if (g) for (const auto &a : g->abilities) if (s.piety >= a.piety_required) result = std::max(result, a.tier);
    return result;
}
invocation_result invoke(state &s, const std::string &id)
{
    validate(s);
    for (const auto &g : registry) for (const auto &a : g.abilities) if (id == a.id) {
        if (s.current != g.id) return invocation_result::wrong_god;
        if (s.piety < a.piety_required) return invocation_result::locked;
        if (a.kind == ability_kind::passive) return invocation_result::passive;
        return invocation_result::not_implemented;
    }
    return invocation_result::unknown_ability;
}
void save_properties(CrawlHashTable &owner, const state &s)
{
    validate(s);
    CrawlHashTable root, gods;
    root["schema"] = s.schema; root["current"] = s.current; root["piety"] = s.piety;
    for (const auto &g : s.per_god) {
        CrawlHashTable t;
        t["joins"] = g.second.joins; t["departures"] = g.second.departures;
        t["mode"] = g.second.mode;
        t["resources"] = numbers(g.second.resources);
        t["cooldown_aut"] = numbers(g.second.cooldown_aut);
        t["duration_aut"] = numbers(g.second.duration_aut);
        gods[g.first] = t;
    }
    root["gods"] = gods;
    owner[property_key] = root;
}
state load_properties(const CrawlHashTable &owner)
{
    state s;
    if (!owner.exists(property_key)) return s;
    const auto &root = field(owner, property_key, SV_HASH).get_table();
    s.schema = field(root, "schema", SV_INT).get_int();
    require(s.schema == 1, "Unsupported HoloCrawl framework schema");
    s.current = field(root, "current", SV_STR).get_string();
    s.piety = field(root, "piety", SV_INT).get_int();
    const auto &gods = field(root, "gods", SV_HASH).get_table();
    require(gods.size() <= 22, "Too many saved Holo gods");
    for (const auto &g : gods) {
        require(find_god(g.first) && g.second.get_type() == SV_HASH, "Unknown or malformed saved Holo god");
        const auto &t = g.second.get_table();
        god_state data;
        data.joins = field(t, "joins", SV_INT).get_int();
        data.departures = field(t, "departures", SV_INT).get_int();
        data.mode = field(t, "mode", SV_STR).get_string();
        data.resources = read_numbers(field(t, "resources", SV_HASH).get_table());
        data.cooldown_aut = read_numbers(field(t, "cooldown_aut", SV_HASH).get_table());
        data.duration_aut = read_numbers(field(t, "duration_aut", SV_HASH).get_table());
        s.per_god[g.first] = data;
    }
    validate(s);
    return s;
}
int command_line(int argc, char **argv)
{
    if (argc < 2) return -1;
    const std::string command(argv[1]);
    if (command != "-holo-los-table" && command != "-holo-los-fixtures"
        && command != "-holo-structure" && command != "-holo-structure-test"
        && command != "-holo-state-write" && command != "-holo-state-read") return -1;
    try {
        if (command == "-holo-los-table") { std::puts(visibility_paths_json().c_str()); return 0; }
        if (command == "-holo-los-fixtures") { std::puts(visibility_fixtures_json().c_str()); return 0; }
        if (command == "-holo-structure") { std::puts(catalog_json); return 0; }
        if (command == "-holo-structure-test") return self_test();
        require(argc == 3, "State fixture command requires one file path");
        const auto expected = encode(fixture());
        if (command == "-holo-state-write") {
            std::ofstream out(argv[2], std::ios::binary | std::ios::trunc);
            require(bool(out), "Cannot create state fixture");
            out.write(reinterpret_cast<const char *>(expected.data()), expected.size());
            require(bool(out), "State fixture write failed");
        } else {
            std::ifstream in(argv[2], std::ios::binary);
            require(bool(in), "Cannot read state fixture");
            std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
            const auto restored = decode(bytes);
            require(encode(restored) == expected, "Fresh process state fixture mismatch");
        }
        std::puts("{\"status\":\"passed\",\"current\":\"suisei\",\"piety\":100,\"stars\":3,\"historyGods\":22,\"scope\":\"framework_native_property_fixture\"}");
        return 0;
    } catch (const std::exception &e) {
        std::fprintf(stderr, "HoloCrawl structure error: %s\n", e.what());
        return 1;
    }
}
}
