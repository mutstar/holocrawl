#include "AppHdr.h"
#ifdef USE_TILE_LOCAL
#include "tiledgnbuf.h"

#include "tile-flags.h"
#include "tiledef-dngn.h"
#include "tiledef-icons.h"
#include "tiledef-main.h"
#include "tiledef-player.h"
#include "tiledoll.h"
#include "holo-visual.h"
#include "tilemcache.h"
#include "tilepick.h"
#include "tiletex.h"
#include "player.h"
#include "state.h"
#include "store.h"

DungeonCellBuffer::DungeonCellBuffer(ImageManager *im) :
    m_buf_floor(&im->m_textures[TEX_FLOOR]),
    m_buf_wall(&im->m_textures[TEX_WALL]),
    m_buf_feat(&im->m_textures[TEX_FEAT]),
    m_buf_feat_trans(&im->m_textures[TEX_FEAT], 17),
    m_buf_holo_ground_vfx(&im->m_textures[TEX_FEAT]),
    m_buf_holo_ground_tint(&im->m_textures[TEX_FEAT]),
    m_buf_doll(&im->m_textures[TEX_PLAYER], 17),
    m_buf_main_trans(&im->m_textures[TEX_DEFAULT], 17),
    m_buf_main(&im->m_textures[TEX_DEFAULT]),
    m_buf_spells(&im->m_textures[TEX_GUI]),
    m_buf_skills(&im->m_textures[TEX_GUI]),
    m_buf_commands(&im->m_textures[TEX_GUI]),
    m_buf_icons(&im->m_textures[TEX_ICONS]),
    m_buf_holo_vfx(&im->m_textures[TEX_FEAT])
{
}

static bool _in_water(const packed_cell &cell)
{
    return (cell.bg & TILE_FLAG_WATER) && !(cell.fg & TILE_FLAG_FLYING);
}

void DungeonCellBuffer::add(const packed_cell &cell, int x, int y)
{
    pack_background(x, y, cell);

    const tileidx_t fg_idx = cell.fg & TILE_FLAG_MASK;
    const bool in_water = _in_water(cell);

    tileidx_t cloud_idx = cell.cloud & TILE_FLAG_MASK;

    // in the shoals, ink is handled in pack_cell_overlays(): don't overdraw
    if (cloud_idx == TILE_CLOUD_INK && player_in_branch(BRANCH_SHOALS))
        cloud_idx = 0;

    if (fg_idx >= TILEP_MCACHE_START)
    {
        mcache_entry *entry = mcache.get(fg_idx);
        if (entry)
            pack_mcache(entry, x, y, in_water);
        else
            m_buf_doll.add(TILEP_MONS_UNKNOWN, x, y, 0, in_water, false);
    }
    else if (fg_idx == TILEP_PLAYER)
        pack_player(x, y, in_water);
    else if (fg_idx >= TILE_MAIN_MAX)
        m_buf_doll.add(fg_idx, x, y, TILEP_PART_MAX, in_water, false);

    pack_foreground(x, y, cell);

    // Draw cloud layer(s)
    if (cloud_idx && cloud_idx < TILE_FEAT_MAX)
    {
        // If there's a foreground, sandwich it between two semi-transparent
        // clouds at different z-indices. This uses the same alpha fading as
        // a swimming characters but applied to the cloud (instead of as normal
        // applied to the character).
        if (fg_idx)
        {
            m_buf_main_trans.add_masked(cloud_idx, x, y, 0, 0, 0, -1, 255, 255, 20);
            m_buf_main_trans.add_masked(cloud_idx, x, y, 50, 0, 0, -1, 15, 255,20);
        }
        else
            // Otherwise render it normally with full transparency
             m_buf_main.add(cloud_idx, x, y);
    }
}

void DungeonCellBuffer::add_sopia_gravity_cell(int x,int y,int dx,int dy,int radius,int frame)
{
    const float p=1.0f/32;
    const VColour haze(123,96,196,30),rim(196,163,249,145),star(247,224,157,210);
    m_buf_holo_range.add(x,y,x+1,y+1,haze);
    // Broken perimeter defines the square gameplay footprint without a full grid.
    for(int i=3;i<30;i+=8) {
        if(dx==-radius)m_buf_holo_range.add(x+p,y+i*p,x+2*p,y+(i+4)*p,rim);
        if(dx==radius)m_buf_holo_range.add(x+30*p,y+i*p,x+31*p,y+(i+4)*p,rim);
        if(dy==-radius)m_buf_holo_range.add(x+i*p,y+p,x+(i+4)*p,y+2*p,rim);
        if(dy==radius)m_buf_holo_range.add(x+i*p,y+30*p,x+(i+4)*p,y+31*p,rim);
    }
    if(!dx && !dy) {
        if(crawl_state.test && you.props.exists("holo_sopia_bigbang_preview")) {
            const int charge=you.props["holo_sopia_bigbang_preview"].get_int();
            if(charge>=1 && charge<=3)for(int i=0;i<charge;++i) {
                const int u=7+8*i,v=5;
                m_buf_holo_range.add(x+(u-2)*p,y+v*p,x+(u+3)*p,y+(v+1)*p,star);
                m_buf_holo_range.add(x+u*p,y+(v-2)*p,x+(u+1)*p,y+(v+3)*p,star);
            }
        }
        return;
    }
    const int sx=(dx>0)-(dx<0),sy=(dy>0)-(dy<0);
    // Four discrete positions travel toward the nucleus, below every actor.
    const int shift=12-8*frame;
    const int u=16+sx*shift/2,v=16+sy*shift/2;
    for(int k=0;k<4;++k) {
        const int a=u+sx*k,b=v+sy*k;
        m_buf_holo_range.add(x+a*p,y+b*p,x+(a+2)*p,y+(b+2)*p,k==0?star:rim);
    }
}

void DungeonCellBuffer::add_vivi_impact_cell(int x,int y)
{
    // Native floor geometry beneath actors; each affected tile stays readable.
    const float p=1.0f/32;
    m_buf_holo_range.add(x+p,y+p,x+1-p,y+1-p,VColour(220,106,239,85));
    const VColour rim(255,190,240,210);
    m_buf_holo_range.add(x+p,y+p,x+1-p,y+3*p,rim);
    m_buf_holo_range.add(x+p,y+1-3*p,x+1-p,y+1-p,rim);
    m_buf_holo_range.add(x+p,y+3*p,x+3*p,y+1-3*p,rim);
    m_buf_holo_range.add(x+1-3*p,y+3*p,x+1-p,y+1-3*p,rim);
}

void DungeonCellBuffer::add_holo_range_cell(int x,int y,bool left_edge,
    bool top_edge,bool right_edge,bool bottom_edge)
{
    // A broken frost rim around the actual footprint, with no internal grid.
    // Inset corner steps soften the silhouette; everything stays under snow
    // and actors. Pure screen geometry: no RNG, combat or map-state changes.
    const float px=1.0f/32.0f;
    const VColour frost(150,220,250,105),haze(137,213,249,28);
    auto dot=[&](int u,int v) {
        m_buf_holo_range.add(x+u*px,y+v*px,x+(u+1)*px,y+(v+1)*px,frost);
    };
    auto edge=[&](bool horizontal,bool far,bool first_corner,bool last_corner) {
        const int start=first_corner?4:0,end=last_corner?28:32;
        for(int i=start;i<end;++i) {
            // Four-pixel icy fragments separated by clear two-pixel gaps.
            if(i%6>=4)continue;
            const int inset=((i/6)%3==1)?1:0;
            const int axis=far?31-inset:inset;
            const int u=horizontal?i:axis,v=horizontal?axis:i;
            dot(u,v);
            const int inner=far?axis-1:axis+1;
            const int hu=horizontal?i:inner,hv=horizontal?inner:i;
            m_buf_holo_range.add(x+hu*px,y+hv*px,x+(hu+1)*px,y+(hv+1)*px,haze);
        }
    };
    if(top_edge)edge(true,false,left_edge,right_edge);
    if(bottom_edge)edge(true,true,left_edge,right_edge);
    if(left_edge)edge(false,false,top_edge,bottom_edge);
    if(right_edge)edge(false,true,top_edge,bottom_edge);
    auto corner=[&](bool right,bool bottom) {
        const int steps[][2]={{3,0},{2,1},{1,2},{0,3}};
        for(const auto &p:steps)dot(right?31-p[0]:p[0],bottom?31-p[1]:p[1]);
    };
    if(left_edge&&top_edge)corner(false,false);
    if(right_edge&&top_edge)corner(true,false);
    if(left_edge&&bottom_edge)corner(false,true);
    if(right_edge&&bottom_edge)corner(true,true);
}

void DungeonCellBuffer::add_holo_vfx_tile(int tileidx,int x,int y,int span_x,int span_y,bool under_actors)
{
    if(tileidx) {
        const auto &inf=tile_feat_info(tileidx);
        const bool nova=tileidx>=TILE_HOLO_FX_SOPIANOVA0 && tileidx<=TILE_HOLO_FX_SOPIANOVA3;
        if(nova || (tileidx>=TILE_HOLO_FX_SOPIAGRAVITY0 && tileidx<=TILE_HOLO_FX_SOPIAGRAVITY3)) {
            // Full-footprint preview, tinted below actors. Texture alpha and
            // vertex opacity multiply; do not alter the generated bitmap.
            const auto *texture=static_cast<const TilesTexture *>(m_buf_holo_ground_tint.current_texture());
            float sx=x,sy=y,ex,ey,tx,ty,ux,uy;
            if(texture->get_coords(tileidx,(inf.width-TILE_X)/2,inf.height-TILE_Y,
                sx,sy,ex,ey,tx,ty,ux,uy,true,-1,-1,float(inf.width)/span_x,float(inf.height)/span_y)) {
                GLWPrim rect(sx,sy,ex,ey);rect.set_tex(tx,ty,ux,uy);
                int opacity=105;
                if(crawl_state.test && you.props.exists("holo_sopia_bigbang_preview")) {
                    const int stage=you.props["holo_sopia_bigbang_preview"].get_int();
                    if(nova) { const int alpha[]={210,210,170,90};opacity=alpha[tileidx-TILE_HOLO_FX_SOPIANOVA0]; }
                    else opacity=105+20*std::min(3,stage);
                }
                rect.set_col(VColour(255,255,255,opacity));m_buf_holo_ground_tint.add_primitive(rect);
                // Readable charge stars sit above the large tinted disc but
                // below actors. Reuse only the generated nova's star core UV.
                if(!nova && crawl_state.test && you.props.exists("holo_sopia_bigbang_preview")) {
                    const int charge=you.props["holo_sopia_bigbang_preview"].get_int();
                    if(charge>=1 && charge<=3) {
                        float a=0,b=0,c,d,u,v,w,z;
                        if(texture->get_coords(TILE_HOLO_FX_SOPIANOVA2,0,0,a,b,c,d,u,v,w,z,true)) {
                            const float du=w-u,dv=z-v;
                            for(int i=0;i<charge;++i) {
                                const float gx=(sx+ex)/2-0.40f+0.28f*i,gy=(sy+ey)/2-0.60f;
                                GLWPrim mark(gx,gy,gx+0.22f,gy+0.22f);
                                mark.set_tex(u+du*0.34f,v+dv*0.34f,u+du*0.66f,v+dv*0.66f);
                                mark.set_col(VColour(255,255,255,245));m_buf_holo_ground_tint.add_primitive(mark);
                            }
                        }
                    }
                }
            }
            return;
        }
        // Native-size ceremonial sprites keep their detail. For ordinary
        // 32x32 tiles these offsets/divisors are identical to the old path.
        auto &buffer=under_actors?m_buf_holo_ground_vfx:m_buf_holo_vfx;
        // Float Polka's performance hat diagonally above the head.
        // Apply to both invocation frames and the persistent status cue.
        const bool polka_hat=tileidx==holo_visual::effect_tile(holo_visual::effect::night_polka1,0)
            || tileidx==holo_visual::effect_tile(holo_visual::effect::night_polka1,1);
        const bool lui_wings=tileidx==holo_visual::effect_tile(holo_visual::effect::night_lui5,0)
            || tileidx==holo_visual::effect_tile(holo_visual::effect::night_lui5,1);
        const bool raden_screen=tileidx==holo_visual::effect_tile(holo_visual::effect::night_raden5,0)
            || tileidx==holo_visual::effect_tile(holo_visual::effect::night_raden5,1)
            || tileidx==holo_visual::effect_tile(holo_visual::effect::night_raden5,2);
        // Native-size backdrops anchor to the player's feet beneath actors.
        const bool native_backdrop=lui_wings || raden_screen;
        const bool hajime_notes=tileidx==holo_visual::effect_tile(holo_visual::effect::night_hajime1,0);
        const bool vivi_gems=(tileidx>=TILE_HOLO_FX_VIVIATTENTION1 && tileidx<=TILE_HOLO_FX_VIVIATTENTION3)
            || tileidx==TILE_HOLO_FX_VIVIENCORE_READY || tileidx==TILE_HOLO_FX_VIVIFINALE_MARK;
        buffer.add(tileidx,x,y,native_backdrop?0:(inf.width-TILE_X)/2+(polka_hat?4:0),native_backdrop?0:inf.height-TILE_Y-(polka_hat?12:(hajime_notes || vivi_gems)?8:0),
            true,-1,native_backdrop?32.0f:float(inf.width)/span_x,native_backdrop?32.0f:float(inf.height)/span_y);
        // Korone's awakening: keep the complete aura beneath actors, then
        // reveal only the two paw glyphs above actors using the same texture.
        // UV cropping preserves every source pixel, position and scale.
        if(under_actors && (tileidx==holo_visual::effect_tile(holo_visual::effect::night_korone5,0)
            || tileidx==holo_visual::effect_tile(holo_visual::effect::night_korone5,1))) {
            const auto *texture=static_cast<const TilesTexture *>(m_buf_holo_vfx.current_texture());
            float sx=x,sy=y,ex,ey,tx,ty,ux,uy;
            if(texture->get_coords(tileidx,(inf.width-TILE_X)/2,inf.height-TILE_Y,
                sx,sy,ex,ey,tx,ty,ux,uy,true,-1,-1,
                float(inf.width)/span_x,float(inf.height)/span_y)) {
                const bool expanded=tileidx==holo_visual::effect_tile(holo_visual::effect::night_korone5,1);
                const float glyph_width=expanded?56:48,glyph_height=expanded?55:47;
                const float glyph_x=80-int(glyph_width)/2,glyph_y=80-int(glyph_height)/2;
                auto paw=[&](float left,float top,float right,float bottom) {
                    // The atlas stores the entire transparent 160px canvas.
                    // Convert glyph-relative bounds to full-canvas UV fractions.
                    left=(glyph_x+glyph_width*left)/inf.width;
                    right=(glyph_x+glyph_width*right)/inf.width;
                    top=(glyph_y+glyph_height*top)/inf.height;
                    bottom=(glyph_y+glyph_height*bottom)/inf.height;
                    GLWPrim rect(sx+(ex-sx)*left,sy+(ey-sy)*top,
                        sx+(ex-sx)*right,sy+(ey-sy)*bottom);
                    rect.set_tex(tx+(ux-tx)*left,ty+(uy-ty)*top,
                        tx+(ux-tx)*right,ty+(uy-ty)*bottom);
                    m_buf_holo_vfx.add_primitive(rect);
                };
                paw(0.0f,0.39f,0.36f,0.82f);
                paw(0.64f,0.39f,1.0f,0.82f);
            }
        }
    }
}

void DungeonCellBuffer::add_monster(const monster_info &mon, int x, int y)
{
    tileidx_t t    = tileidx_monster(mon);
    tileidx_t t0   = t & TILE_FLAG_MASK;
    tileidx_t flag = t & (~TILE_FLAG_MASK);

    // Copied from _tile_place_monster()
    if (!mons_class_is_stationary(mon.type) || mon.type == MONS_TRAINING_DUMMY)
    {
        tileidx_t mcache_idx = mcache.register_monster(mon);
        t = flag | (mcache_idx ? mcache_idx : t0);
        t0 = t & TILE_FLAG_MASK;
    }

    // Copied from ::add()
    if (t0 >= TILEP_MCACHE_START)
    {
        mcache_entry *entry = mcache.get(t0);
        if (entry)
            pack_mcache(entry, x, y, false);
        else
            m_buf_doll.add(TILEP_MONS_UNKNOWN, x, y, 0, false, false);
    }
    else if (t0 >= TILE_MAIN_MAX)
        m_buf_doll.add(t0, x, y, TILEP_PART_MAX, false, false);
    else if (t0 && t0 <= TILE_MAIN_MAX)
    {
        const tileidx_t base_idx = tileidx_known_base_item(t0);
        if (base_idx)
            m_buf_main.add(base_idx, x, y);
        m_buf_main.add(t0, x, y);
    }

    // hijack pack_foreground() to draw status icons
    packed_cell fake_cell;
    fake_cell.fg = flag;
    fake_cell.bg = 0;
    pack_foreground(x, y, fake_cell);
}

void DungeonCellBuffer::add_dngn_tile(int tileidx, int x, int y,
                                      bool in_water)
{
    ASSERT(tileidx < TILE_FEAT_MAX);

    if (tileidx < TILE_FLOOR_MAX)
        m_buf_floor.add(tileidx, x, y);
    else if (tileidx < TILE_WALL_MAX)
        m_buf_wall.add(tileidx, x, y);
    else if (in_water)
    {
        m_buf_floor.add(TILE_DNGN_SHALLOW_WATER, x, y);
        m_buf_feat_trans.add(tileidx, x, y, 0, true, false);
    }
    else
        m_buf_feat.add(tileidx, x, y);
}

void DungeonCellBuffer::add_main_tile(int tileidx, int x, int y)
{
    tileidx_t base = tileidx_known_base_item(tileidx);
    if (base)
        m_buf_main.add(base, x, y);

    m_buf_main.add(tileidx, x, y);
}

void DungeonCellBuffer::add_main_tile(int tileidx, int x, int y, int ox, int oy)
{
    tileidx_t base = tileidx_known_base_item(tileidx);
    if (base)
        m_buf_main.add(base, x, y, ox, oy, false);

    m_buf_main.add(tileidx, x, y, ox, oy, false);
}

void DungeonCellBuffer::add_spell_tile(int tileidx, int x, int y)
{
    m_buf_spells.add(tileidx, x, y);
}

void DungeonCellBuffer::add_skill_tile(int tileidx, int x, int y)
{
    m_buf_skills.add(tileidx, x, y);
}

void DungeonCellBuffer::add_command_tile(int tileidx, int x, int y)
{
    m_buf_commands.add(tileidx, x, y);
}

void DungeonCellBuffer::add_icons_tile(int tileidx, int x, int y)
{
    m_buf_icons.add(tileidx, x, y);
}

void DungeonCellBuffer::add_icons_tile(int tileidx, int x, int y,
                                       int ox, int oy)
{
    m_buf_icons.add(tileidx, x, y, ox, oy, false);
}

void DungeonCellBuffer::clear()
{
    m_buf_floor.clear();
    m_buf_holo_range.clear();
    m_buf_wall.clear();
    m_buf_feat.clear();
    m_buf_feat_trans.clear();
    m_buf_holo_ground_vfx.clear();
    m_buf_holo_ground_tint.clear();
    m_buf_doll.clear();
    m_buf_main_trans.clear();
    m_buf_main.clear();
    m_buf_spells.clear();
    m_buf_skills.clear();
    m_buf_commands.clear();
    m_buf_icons.clear();
    m_buf_holo_vfx.clear();
}

void DungeonCellBuffer::draw()
{
    m_buf_floor.draw();
    m_buf_wall.draw();
    m_buf_holo_range.draw();
    m_buf_feat.draw();
    m_buf_feat_trans.draw();
    // Large garden bloom belongs below every actor and its status/HP marks.
    m_buf_holo_ground_vfx.draw();
    m_buf_holo_ground_tint.draw();
    m_buf_doll.draw();
    m_buf_main_trans.draw();
    m_buf_main.draw();
    m_buf_skills.draw();
    m_buf_spells.draw();
    m_buf_commands.draw();
    m_buf_icons.draw();
    m_buf_holo_vfx.draw();
}

void DungeonCellBuffer::add_blood_overlay(int x, int y, const packed_cell &cell,
                                          bool is_wall)
{
    if (cell.is_liquefied && !is_wall)
    {
        int offset = cell.flv.special % tile_dngn_count(TILE_LIQUEFACTION);
        m_buf_floor.add(TILE_LIQUEFACTION + offset, x, y);
    }
    else if (cell.is_bloody)
    {
        tileidx_t basetile;
        if (is_wall)
        {
            basetile = cell.old_blood ? TILE_WALL_OLD_BLOOD : TILE_WALL_BLOOD_S;
            basetile += tile_dngn_count(basetile) * cell.blood_rotation;
        }
        else
            basetile = TILE_BLOOD;
        const int offset = cell.flv.special % tile_dngn_count(basetile);
        m_buf_feat.add(basetile + offset, x, y);
    }
}

void DungeonCellBuffer::pack_background(int x, int y, const packed_cell &cell)
{
    const tileidx_t bg = cell.bg;
    const tileidx_t bg_idx = cell.bg & TILE_FLAG_MASK;

    if (bg_idx >= TILE_DNGN_FIRST_TRANSPARENT)
        add_dngn_tile(cell.flv.floor, x, y);

    // Draw blood beneath feature tiles.
    if (bg_idx > TILE_WALL_MAX)
        add_blood_overlay(x, y, cell);

    add_dngn_tile(bg_idx, x, y, cell.mangrove_water);

    if (bg_idx > TILE_DNGN_UNSEEN)
    {
        // Draw blood on top of wall tiles.
        if (bg_idx <= TILE_WALL_MAX)
            add_blood_overlay(x, y, cell, bg_idx >= TILE_FLOOR_MAX);

        for (int i = 0; i < cell.num_dngn_overlay; ++i)
            add_dngn_tile(cell.dngn_overlay[i], x, y);

        if (!(bg & TILE_FLAG_UNSEEN))
        {
            // Add tentacle corner overlays.
            if (bg & TILE_FLAG_TENTACLE_NW)
            {
                if (bg & TILE_FLAG_TENTACLE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_OVERLAY_NW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ELDRITCH)
                    m_buf_feat.add(TILE_ELDRITCH_OVERLAY_NW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_STARSPAWN)
                    m_buf_feat.add(TILE_STARSPAWN_OVERLAY_NW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_VINE)
                    m_buf_feat.add(TILE_VINE_OVERLAY_NW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ZOMBIE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_ZOMBIE_OVERLAY_NW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SIMULACRUM_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SIMULACRUM_OVERLAY_NW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SPECTRAL_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SPECTRAL_OVERLAY_NW, x, y);
            }
            else if (bg & TILE_FLAG_TENTACLE_NE)
            {
                if (bg & TILE_FLAG_TENTACLE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_OVERLAY_NE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ELDRITCH)
                    m_buf_feat.add(TILE_ELDRITCH_OVERLAY_NE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_STARSPAWN)
                    m_buf_feat.add(TILE_STARSPAWN_OVERLAY_NE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_VINE)
                    m_buf_feat.add(TILE_VINE_OVERLAY_NE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ZOMBIE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_ZOMBIE_OVERLAY_NE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SIMULACRUM_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SIMULACRUM_OVERLAY_NE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SPECTRAL_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SPECTRAL_OVERLAY_NE, x, y);
            }
            else if (bg & TILE_FLAG_TENTACLE_SW)
            {
                if (bg & TILE_FLAG_TENTACLE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_OVERLAY_SW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ELDRITCH)
                    m_buf_feat.add(TILE_ELDRITCH_OVERLAY_SW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_STARSPAWN)
                    m_buf_feat.add(TILE_STARSPAWN_OVERLAY_SW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_VINE)
                    m_buf_feat.add(TILE_VINE_OVERLAY_SW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ZOMBIE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_ZOMBIE_OVERLAY_SW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SIMULACRUM_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SIMULACRUM_OVERLAY_SW, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SPECTRAL_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SPECTRAL_OVERLAY_SW, x, y);
            }
            else if (bg & TILE_FLAG_TENTACLE_SE)
            {
                if (bg & TILE_FLAG_TENTACLE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_OVERLAY_SE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ELDRITCH)
                    m_buf_feat.add(TILE_ELDRITCH_OVERLAY_SE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_STARSPAWN)
                    m_buf_feat.add(TILE_STARSPAWN_OVERLAY_SE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_VINE)
                    m_buf_feat.add(TILE_VINE_OVERLAY_SE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_ZOMBIE_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_ZOMBIE_OVERLAY_SE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SIMULACRUM_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SIMULACRUM_OVERLAY_SE, x, y);
                else if (bg & TILE_FLAG_TENTACLE_SPECTRAL_KRAKEN)
                    m_buf_feat.add(TILE_KRAKEN_SPECTRAL_OVERLAY_SE, x, y);
            }
        }

        if (!(bg & TILE_FLAG_UNSEEN))
        {
            if (cell.is_sanctuary)
                m_buf_feat.add(TILE_SANCTUARY, x, y);
#if TAG_MAJOR_VERSION == 34
            if (cell.heat_aura)
                m_buf_feat.add(TILE_HEAT_AURA + cell.heat_aura - 1, x, y);
#endif
            if (cell.is_silenced)
                m_buf_feat.add(TILE_SILENCED, x, y);
            if (cell.halo == HALO_RANGE)
                m_buf_feat.add(TILE_HALO_RANGE, x, y);
            if (cell.halo == HALO_UMBRA)
                m_buf_feat.add(TILE_UMBRA + random2(4), x, y);

            if (cell.orb_glow)
                m_buf_feat.add(TILE_ORB_GLOW + cell.orb_glow - 1, x, y);
            if (cell.quad_glow)
                m_buf_feat.add(TILE_QUAD_GLOW, x, y);
            if (cell.disjunct)
                m_buf_feat.add(TILE_DISJUNCT + cell.disjunct - 1, x, y);
            if (cell.awakened_forest)
                m_buf_icons.add(TILEI_BERSERK, x, y);

            if (cell.fg)
            {
                const tileidx_t att_flag = cell.fg & TILE_FLAG_ATT_MASK;
                if (att_flag == TILE_FLAG_PET)
                    m_buf_feat.add(TILE_HALO_FRIENDLY, x, y);
                else if (att_flag == TILE_FLAG_GD_NEUTRAL)
                    m_buf_feat.add(TILE_HALO_GD_NEUTRAL, x, y);
                else if (att_flag == TILE_FLAG_NEUTRAL)
                    m_buf_feat.add(TILE_HALO_NEUTRAL, x, y);

                if (cell.is_highlighted_summoner)
                    m_buf_feat.add(TILE_HALO_SUMMONER, x, y);
            }

            // Apply the travel exclusion under the foreground if the cell is
            // visible. It will be applied later if the cell is unseen.
            if (bg & TILE_FLAG_EXCL_CTR)
                m_buf_feat.add(TILE_TRAVEL_EXCLUSION_CENTRE_BG, x, y);
            else if (bg & TILE_FLAG_TRAV_EXCL)
                m_buf_feat.add(TILE_TRAVEL_EXCLUSION_BG, x, y);
        }

    }

    // allow rays even on completely unseen squares (e.g. passwall)
    if (bg & TILE_FLAG_RAY)
        m_buf_feat.add(TILE_RAY, x, y);
    else if (bg & TILE_FLAG_RAY_OOR)
        m_buf_feat.add(TILE_RAY_OUT_OF_RANGE, x, y);
    else if (bg & TILE_FLAG_LANDING)
        m_buf_feat.add(TILE_LANDING, x, y);
    else if (bg & TILE_FLAG_RAY_MULTI)
        m_buf_feat.add(TILE_RAY_MULTI, x, y);
}

void DungeonCellBuffer::pack_foreground(int x, int y, const packed_cell &cell)
{
    const tileidx_t fg = cell.fg;
    const tileidx_t bg = cell.bg;
    const tileidx_t fg_idx = cell.fg & TILE_FLAG_MASK;
    const bool in_water = _in_water(cell);

    if (fg_idx && fg_idx <= TILE_MAIN_MAX)
    {
        const tileidx_t base_idx = tileidx_known_base_item(fg_idx);

        if (in_water)
        {
            if (base_idx)
                m_buf_main_trans.add(base_idx, x, y, 0, true, false);
            m_buf_main_trans.add(fg_idx, x, y, 0, true, false);
        }
        else
        {
            if (base_idx)
                m_buf_main.add(base_idx, x, y);

            m_buf_main.add(fg_idx, x, y);
        }
    }

    if (fg & TILE_FLAG_NET)
        m_buf_icons.add(TILEI_TRAP_NET, x, y);

    if (fg & TILE_FLAG_WEB)
        m_buf_icons.add(TILEI_TRAP_WEB, x, y);

    if (fg & TILE_FLAG_S_UNDER)
        m_buf_icons.add(TILEI_SOMETHING_UNDER, x, y);

    // Pet mark
    if (fg & TILE_FLAG_ATT_MASK)
    {
        const tileidx_t att_flag = fg & TILE_FLAG_ATT_MASK;
        if (att_flag == TILE_FLAG_PET)
            m_buf_icons.add(TILEI_FRIENDLY, x, y);
        else if (att_flag == TILE_FLAG_GD_NEUTRAL)
            m_buf_icons.add(TILEI_GOOD_NEUTRAL, x, y);
        else if (att_flag == TILE_FLAG_NEUTRAL)
            m_buf_icons.add(TILEI_NEUTRAL, x, y);
    }

    //The berserk icon is in the lower right, so status_shift doesn't need changing.
    if (fg & TILE_FLAG_BERSERK)
        m_buf_icons.add(TILEI_BERSERK, x, y);
    // ditto ideal
    if (fg & TILE_FLAG_IDEALISED)
        m_buf_icons.add(TILEI_IDEALISED, x, y);

    int status_shift = 0;
    if (fg & TILE_FLAG_BEH_MASK)
    {
        const tileidx_t beh_flag = fg & TILE_FLAG_BEH_MASK;
        if (beh_flag == TILE_FLAG_STAB)
        {
            m_buf_icons.add(TILEI_STAB_BRAND, x, y);
            status_shift += 12;
        }
        else if (beh_flag == TILE_FLAG_MAY_STAB)
        {
            m_buf_icons.add(TILEI_MAY_STAB_BRAND, x, y);
            status_shift += 7;
        }
        else if (beh_flag == TILE_FLAG_FLEEING)
        {
            m_buf_icons.add(TILEI_FLEEING, x, y);
            status_shift += 3;
        }
    }

    if (fg & TILE_FLAG_POISON)
    {
        m_buf_icons.add(TILEI_POISON, x, y, -status_shift, 0);
        status_shift += 5;
    }
    if (fg & TILE_FLAG_STICKY_FLAME)
    {
        m_buf_icons.add(TILEI_STICKY_FLAME, x, y, -status_shift, 0);
        status_shift += 7;
    }
    if (fg & TILE_FLAG_INNER_FLAME)
    {
        m_buf_icons.add(TILEI_INNER_FLAME, x, y, -status_shift, 0);
        status_shift += 7;
    }
    if (fg & TILE_FLAG_CONSTRICTED)
    {
        m_buf_icons.add(TILEI_CONSTRICTED, x, y, -status_shift, 0);
        status_shift += 11;
    }
    if (fg & TILE_FLAG_GLOWING)
    {
        //if (!cell.halo)
        //    m_buf_feat.add(TILE_HALO, x, y);

        m_buf_icons.add(TILEI_GLOWING, x, y, -status_shift, 0);
        status_shift += 7;
    }
    if (fg & TILE_FLAG_HASTED)
    {
        m_buf_icons.add(TILEI_HASTED, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_SLOWED)
    {
        m_buf_icons.add(TILEI_SLOWED, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_MIGHT)
    {
        m_buf_icons.add(TILEI_MIGHT, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_DRAIN)
    {
        m_buf_icons.add(TILEI_DRAIN, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_PAIN_MIRROR)
    {
        m_buf_icons.add(TILEI_PAIN_MIRROR, x, y, -status_shift, 0);
        status_shift += 7;
    }
    if (fg & TILE_FLAG_PETRIFYING)
    {
        m_buf_icons.add(TILEI_PETRIFYING, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_PETRIFIED)
    {
        m_buf_icons.add(TILEI_PETRIFIED, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_BLIND)
    {
        m_buf_icons.add(TILEI_BLIND, x, y, -status_shift, 0);
        status_shift += 10;
    }
    if (fg & TILE_FLAG_DEATHS_DOOR)
    {
        m_buf_icons.add(TILEI_DEATHS_DOOR, x, y, -status_shift, 0);
        status_shift += 10;
    }
    if (fg & TILE_FLAG_BOUND_SOUL)
    {
        m_buf_icons.add(TILEI_BOUND_SOUL, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_INFESTED)
    {
        m_buf_icons.add(TILEI_INFESTED, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_CORRODED)
    {
        m_buf_icons.add(TILEI_CORRODED, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_SWIFT)
    {
        m_buf_icons.add(TILEI_SWIFT, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_PINNED)
    {
        m_buf_icons.add(TILEI_PINNED, x, y, -status_shift, 0);
        status_shift += 6;
    }
    if (fg & TILE_FLAG_RECALL)
    {
        m_buf_icons.add(TILEI_RECALL, x, y, -status_shift, 0);
        status_shift += 9;
    }
    if (fg & TILE_FLAG_VILE_CLUTCH)
    {
        m_buf_icons.add(TILEI_VILE_CLUTCH, x, y, -status_shift, 0);
        status_shift += 11;
    }
    if (fg & TILE_FLAG_POSSESSABLE)
    {
        m_buf_icons.add(TILEI_POSSESSABLE, x, y, -status_shift, 0);
        status_shift += 6;
    }

    // Summoned and anim. weap. icons will overlap if you have a
    // summoned dancing weapon, but that's rare and still looks okay.
    if (fg & TILE_FLAG_ANIM_WEP)
        m_buf_icons.add(TILEI_ANIMATED_WEAPON, x, y);
    if (fg & TILE_FLAG_SUMMONED)
        m_buf_icons.add(TILEI_SUMMONED, x, y);
    if (fg & TILE_FLAG_PERM_SUMMON)
        m_buf_icons.add(TILEI_PERM_SUMMON, x, y);

    if (bg & TILE_FLAG_UNSEEN && (bg != TILE_FLAG_UNSEEN || fg))
        m_buf_icons.add(TILEI_MESH, x, y);

    if (bg & TILE_FLAG_OOR && (bg != TILE_FLAG_OOR || fg))
        m_buf_icons.add(TILEI_OOR_MESH, x, y);

    if (bg & TILE_FLAG_MM_UNSEEN && (bg != TILE_FLAG_MM_UNSEEN || fg))
        m_buf_icons.add(TILEI_MAGIC_MAP_MESH, x, y);

    // Don't let the "new stair" icon cover up any existing icons, but
    // draw it otherwise.
    if (bg & TILE_FLAG_NEW_STAIR && status_shift == 0)
        m_buf_icons.add(TILEI_NEW_STAIR, x, y);

    if (bg & TILE_FLAG_NEW_TRANSPORTER && status_shift == 0)
        m_buf_icons.add(TILEI_NEW_TRANSPORTER, x, y);

    if (bg & TILE_FLAG_EXCL_CTR && (bg & TILE_FLAG_UNSEEN))
        m_buf_icons.add(TILEI_TRAVEL_EXCLUSION_CENTRE_FG, x, y);
    else if (bg & TILE_FLAG_TRAV_EXCL && (bg & TILE_FLAG_UNSEEN))
        m_buf_icons.add(TILEI_TRAVEL_EXCLUSION_FG, x, y);

    // Tutorial cursor takes precedence over other cursors.
    if (bg & TILE_FLAG_TUT_CURSOR)
        m_buf_icons.add(TILEI_TUTORIAL_CURSOR, x, y);
    else if (bg & TILE_FLAG_CURSOR)
    {
        int type = ((bg & TILE_FLAG_CURSOR) == TILE_FLAG_CURSOR1) ?
            TILEI_CURSOR : TILEI_CURSOR2;

        if ((bg & TILE_FLAG_CURSOR) == TILE_FLAG_CURSOR3)
           type = TILEI_CURSOR3;

        m_buf_icons.add(type, x, y);
    }

    if (cell.travel_trail & 0xF)
    {
        m_buf_icons.add(TILEI_TRAVEL_PATH_FROM +
                        (cell.travel_trail & 0xF) - 1, x, y);
    }
    if (cell.travel_trail & 0xF0)
    {
        m_buf_icons.add(TILEI_TRAVEL_PATH_TO +
                        ((cell.travel_trail & 0xF0) >> 4) - 1, x, y);
    }

    if (fg & TILE_FLAG_MDAM_MASK)
    {
        tileidx_t mdam_flag = fg & TILE_FLAG_MDAM_MASK;
        if (mdam_flag == TILE_FLAG_MDAM_LIGHT)
            m_buf_icons.add(TILEI_MDAM_LIGHTLY_DAMAGED, x, y);
        else if (mdam_flag == TILE_FLAG_MDAM_MOD)
            m_buf_icons.add(TILEI_MDAM_MODERATELY_DAMAGED, x, y);
        else if (mdam_flag == TILE_FLAG_MDAM_HEAVY)
            m_buf_icons.add(TILEI_MDAM_HEAVILY_DAMAGED, x, y);
        else if (mdam_flag == TILE_FLAG_MDAM_SEV)
            m_buf_icons.add(TILEI_MDAM_SEVERELY_DAMAGED, x, y);
        else if (mdam_flag == TILE_FLAG_MDAM_ADEAD)
            m_buf_icons.add(TILEI_MDAM_ALMOST_DEAD, x, y);
    }

    if (fg & TILE_FLAG_DEMON)
    {
        tileidx_t demon_flag = fg & TILE_FLAG_DEMON;
        if (demon_flag == TILE_FLAG_DEMON_1)
            m_buf_icons.add(TILEI_DEMON_NUM1, x, y);
        else if (demon_flag == TILE_FLAG_DEMON_2)
            m_buf_icons.add(TILEI_DEMON_NUM2, x, y);
        else if (demon_flag == TILE_FLAG_DEMON_3)
            m_buf_icons.add(TILEI_DEMON_NUM3, x, y);
        else if (demon_flag == TILE_FLAG_DEMON_4)
            m_buf_icons.add(TILEI_DEMON_NUM4, x, y);
        else if (demon_flag == TILE_FLAG_DEMON_5)
            m_buf_icons.add(TILEI_DEMON_NUM5, x, y);
    }
}

void DungeonCellBuffer::pack_player(int x, int y, bool submerged)
{
    dolls_data result = player_doll;
    fill_doll_equipment(result);
    holo_visual::style_player(result);
    pack_doll(result, x, y, submerged, false);
}

void DungeonCellBuffer::pack_doll(const dolls_data &doll, int x, int y,
                                  bool submerged, bool ghost)
{
    pack_doll_buf(m_buf_doll, doll, x, y, submerged, ghost);
}

void DungeonCellBuffer::pack_mcache(mcache_entry *entry, int x, int y,
                                    bool submerged)
{
    ASSERT(entry);

    bool trans = entry->transparent();

    const dolls_data *doll = entry->doll();
    if (doll)
        pack_doll(*doll, x, y, submerged, trans);

    tile_draw_info dinfo[mcache_entry::MAX_INFO_COUNT];
    int draw_info_count = entry->info(&dinfo[0]);
    for (int i = 0; i < draw_info_count; i++)
    {
        m_buf_doll.add(dinfo[i].idx, x, y, TILEP_PART_MAX, submerged, trans,
                       dinfo[i].ofs_x, dinfo[i].ofs_y);
    }
}
#endif //TILEDGNBUF.CC
