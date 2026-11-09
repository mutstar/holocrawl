#ifdef USE_TILE_LOCAL
#pragma once

#include "tilebuf.h"
#include "tilecell.h"

struct dolls_data;
class mcache_entry;

class ImageManager;

// A set of buffers that takes as input the foreground/background pair
// of tiles from tile_fg/tile_bg and populates a set of tile buffers
// so that the stack of tiles it represents can be easily drawn.
//
// This class should access as little global state as possible.
// If more information needs to be shared to draw, then either add
// a foreground or background flag, or add a member to packed_cell.
class DungeonCellBuffer
{
public:
    DungeonCellBuffer(ImageManager *im);

    void add(const packed_cell &cell, int x, int y);
    void add_monster(const monster_info &mon, int x, int y);
    void add_vivi_impact_cell(int x,int y);
    void add_mela_breath_cell(int x,int y);
    void add_mela_beam_tile(int tileidx,int x,int y,int distance);
    void add_sopia_gravity_cell(int x,int y,int dx,int dy,int radius,int frame);
    void add_holo_range_cell(int x,int y,bool left_edge,bool top_edge,
                             bool right_edge,bool bottom_edge);
    void add_holo_vfx_tile(int tileidx,int x,int y,int span_x=1,int span_y=1,bool under_actors=false);
    void add_dngn_tile(int tileidx, int x, int y, bool in_water = false);
    void add_main_tile(int tileidx, int x, int y);
    void add_main_tile(int tileidx, int x, int y, int ox, int oy);
    void add_spell_tile(int tileidx, int x, int y);
    void add_skill_tile(int tileidx, int x, int y);
    void add_command_tile(int tileidx, int x, int y);
    void add_icons_tile(int tileidx, int x, int y);
    void add_icons_tile(int tileidx, int x, int y, int ox, int oy);

    void clear();
    void draw();

protected:
    void add_blood_overlay(int x, int y, const packed_cell &cell,
                           bool is_wall = false);
    void pack_background(int x, int y, const packed_cell &cell);
    void pack_foreground(int x, int y, const packed_cell &cell);

    void pack_mcache(mcache_entry *entry, int x, int y, bool submerged);
    void pack_player(int x, int y, bool submerged);
    void pack_doll(const dolls_data &doll, int x, int y,
                   bool submerged, bool ghost);

    TileBuffer m_buf_floor;
    TileBuffer m_buf_wall;
    ShapeBuffer m_buf_holo_range;
    TileBuffer m_buf_feat;
    SubmergedTileBuffer m_buf_feat_trans;
    TileBuffer m_buf_holo_ground_vfx;
    ColouredTileBuffer m_buf_holo_ground_tint;
    SubmergedTileBuffer m_buf_doll;
    SubmergedTileBuffer m_buf_main_trans;
    TileBuffer m_buf_main;
    TileBuffer m_buf_spells;
    TileBuffer m_buf_skills;
    TileBuffer m_buf_commands;
    TileBuffer m_buf_icons;
    TileBuffer m_buf_holo_vfx;
};

#endif
