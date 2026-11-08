#include "AppHdr.h"
#include "holo34-visibility.h"
#include "los.h"
#include "ray.h"
#include <set>
#include <sstream>
#include <stdexcept>

namespace holo34 {
namespace {
class clear_opacity : public opacity_func {
public:
    CLONE(clear_opacity)
    opacity_type operator()(const coord_def &) const override { return OPC_CLEAR; }
};
class fixture_opacity : public opacity_func {
public:
    std::vector<std::string> rows;
    CLONE(fixture_opacity)
    opacity_type operator()(const coord_def &p) const override
    {
        if (p.y < 0 || p.y >= static_cast<int>(rows.size()) || p.x < 0
            || p.x >= static_cast<int>(rows[p.y].size())) return OPC_OPAQUE;
        return rows[p.y][p.x] == '#' ? OPC_OPAQUE : rows[p.y][p.x] == '~' ? OPC_HALF : OPC_CLEAR;
    }
};
}
std::string visibility_paths_json()
{
    std::ostringstream out;
    out << "{\"engine\":\"0.34.1\",\"method\":\"native find_ray minimal footprints\",\"maxRadius\":"
        << LOS_RADIUS << ",\"defaultRadius\":" << LOS_DEFAULT_RANGE
        << ",\"metric\":\"chebyshev\",\"footprints\":[";
    const coord_def source(30, 30);
    const clear_opacity clear;
    bool first_target = true;
    for (int y = 0; y <= LOS_RADIUS; ++y) for (int x = 0; x <= LOS_RADIUS; ++x) {
        if (x == 0 && y == 0) continue;
        if (!first_target) out << ',';
        first_target = false;
        out << "{\"target\":[" << x << ',' << y << "],\"paths\":[";
        const coord_def target = source + coord_def(x, y);
        std::set<int> used;
        ray_def ray;
        bool first_path = true;
        while (find_ray(source, target, ray, clear, LOS_RADIUS, !used.empty())) {
            if (!used.insert(ray.cycle_idx).second) break;
            if (used.size() > 512) throw std::runtime_error("Unexpected native ray cycle");
            if (!first_path) out << ',';
            first_path = false;
            out << '[';
            ray_def cursor(ray);
            int steps = 0;
            while (cursor.pos() != target) {
                if (!cursor.advance() || ++steps > 64)
                    throw std::runtime_error("Native visibility footprint failed");
                const auto p = cursor.pos() - source;
                if (steps > 1) out << ',';
                out << '[' << p.x << ',' << p.y << ']';
            }
            out << ']';
        }
        if (first_path) throw std::runtime_error("Native target has no visibility paths");
        out << "]}";
    }
    out << "]}";
    return out.str();
}
std::string visibility_fixtures_json()
{
    std::ostringstream out;
    out << "{\"engine\":\"0.34.1\",\"method\":\"native losight oracle\",\"cases\":[";
    uint32_t rng = 0x34c0ffee;
    const coord_def source(9, 9);
    for (int n = 0; n < 76; ++n) {
        fixture_opacity opc;
        opc.rows.assign(19, std::string(19, '.'));
        for (int y = 0; y < 19; ++y) for (int x = 0; x < 19; ++x) {
            rng = rng * 1664525u + 1013904223u;
            if (n >= 4) opc.rows[y][x] = rng % 100 < 23 ? '#' : rng % 100 < 31 ? '~' : '.';
            if (x == 0 || y == 0 || x == 18 || y == 18) opc.rows[y][x] = '#';
        }
        if (n == 1) { opc.rows[9][10] = '#'; opc.rows[10][9] = '#'; }
        if (n == 2) for (int y = 0; y < 19; ++y) opc.rows[y][10] = '#';
        if (n == 3) { for (int y = 0; y < 19; ++y) opc.rows[y][11] = '~';
                      for (int y = 0; y < 19; ++y) opc.rows[y][12] = '~'; }
        opc.rows[9][9] = '.';
        los_grid visible;
        losight(visible, source, opc, circle_def(7, C_SQUARE));
        if (n) out << ',';
        out << "{\"id\":" << n << ",\"source\":[9,9],\"radius\":7,\"rows\":[";
        for (int y = 0; y < 19; ++y) { if (y) out << ','; out << '"' << opc.rows[y] << '"'; }
        out << "],\"visible\":[";
        for (int y = 0; y < 19; ++y) {
            if (y) out << ',';
            out << '"';
            for (int x = 0; x < 19; ++x) {
                const auto delta = coord_def(x, y) - source;
                out << (delta.rdist() <= 7 && visible(delta) ? '1' : '0');
            }
            out << '"';
        }
        out << "]}";
    }
    out << "]}";
    return out.str();
}
}
