// Native0.34.1 command/LOS checks, used only by the isolated scripted test.
void city_probe107(const std::string &directory,uint64_t seed,int depth)
{
    rng::subgenerator private_rng(seed+depth,0x504c4159313037ULL);
    const coord_def saved_pos=you.pos();
    std::vector<dungeon_feature_type> original_terrain;for(int y=0;y<GYM;++y)for(int x=0;x<GXM;++x)original_terrain.push_back(env.grid(coord_def(x,y)));
    you.hp=you.hp_max=100;you.experience_level=15;you.on_current_level=true;
    for(int i=0;i<NUM_STATS;++i)you.base_stats[i]=20;
    std::vector<coord_def> floors,points;
    int blocked_cells=0,pass_cells=0;
    for(rectangle_iterator it(1);it;++it){
        const auto p=*it;const auto f=env.grid(p);
        if(you.can_pass_through_feat(f)){
            ++pass_cells;if(f==DNGN_FLOOR)floors.push_back(p);
        }else ++blocked_cells;
    }
    check(floors.size()>10,"107 needs walkable cells");
    const int selected=env.properties[facility_key].get_int();
    const auto origin=selected>=0?env.properties[origin_key].get_coord():floors.front();
    const coord_def dirs[]={{-1,-1},{0,-1},{1,-1},{-1,0},{1,0},{-1,1},{0,1},{1,1}};
    // Flood with the native player's feature passability; doors are interactive
    // edges, not permanent walls. Ordinary diagonal stepping is tested below.
    std::queue<coord_def> q;std::set<coord_def> reachable;
    q.push(floors.front());reachable.insert(floors.front());
    while(!q.empty()){
        const auto p=q.front();q.pop();
        for(const auto &d:dirs){const auto n=p+d;
            if(in_bounds(n)&&!reachable.count(n)
                &&(you.can_pass_through_feat(env.grid(n))||feat_is_closed_door(env.grid(n)))){
                reachable.insert(n);q.push(n);
            }
        }
    }
    for(const auto &p:floors)check(reachable.count(p),"107 unreachable walkable floor");
    if(selected>=0){const auto &f=facilities[selected];
        for(int y=0;y<f.height;++y)for(int x=0;x<f.width;++x){
            const auto p=origin+coord_def(x,y);const char c=f.rows[y][x];
            check(env.grid(p)==native_feature(c),"107 facility collision mismatch");
            if(c=='.'||c=='+')check(reachable.count(p),"107 facility interior or entry unreachable");
            else check(!you.can_pass_through_feat(env.grid(p)),"107 blocked fixture became passable");
            if(c=='G'||c=='F')check(opc_default(p)==OPC_CLEAR,"107 transparent fixture blocks LOS");
            if(c=='.'&&points.size()<14)points.push_back(p);
        }
    }
    for(size_t i=0;i<floors.size();i+=std::max(size_t(1),floors.size()/12))points.push_back(floors[i]);
    std::ostringstream out;out<<"{\"seed\":"<<seed<<",\"depth\":"<<depth<<",\"frames\":[";bool first=true;
    const auto frame=[&](const coord_def &p,const char *label){
        los_grid seen;losight(seen,p,opc_default,circle_def(7,C_SQUARE));
        if(!first)out<<',';
        first=false;
        out<<"{\"label\":\""<<label<<"\",\"player\":["<<p.x<<','<<p.y<<"],\"visible\":[";
        for(int y=0;y<GYM;++y){if(y)out<<',';out<<'"';for(int x=0;x<GXM;++x){const coord_def delta=coord_def(x,y)-p;out<<((delta.rdist()<=7&&seen(delta))?'1':'0');}out<<'"';}
        out<<"],\"opacity\":[";
        for(int y=0;y<GYM;++y){if(y)out<<',';out<<'"';for(int x=0;x<GXM;++x)out<<int(opc_default(coord_def(x,y)));out<<'"';}
        out<<"]}";
    };
    for(const auto &p:points)frame(p,"native-los");
    int walked=0,stopped=0,doors=0,los_doors=0,corner_tested=0,corner_allowed=0;
    for(const auto &p:floors){
        for(const auto &d:dirs){const auto n=p+d;if(!in_bounds(n))continue;
            const auto f=env.grid(n);
            if(walked<5&&f==DNGN_FLOOR){you.move_to(p,MV_INTERNAL);you.turn_is_over=false;move_player_action(d);check(you.pos()==n,"107 actual movement command failed");++walked;}
            if(stopped<5&&feat_is_solid(f)){you.move_to(p,MV_INTERNAL);you.turn_is_over=false;move_player_action(d);check(you.pos()==p,"107 actual movement entered a wall/fixture");++stopped;}
            if(!corner_tested&&d.x&&d.y&&f==DNGN_FLOOR
                &&feat_is_solid(env.grid(p+coord_def(d.x,0)))&&feat_is_solid(env.grid(p+coord_def(0,d.y)))){
                you.move_to(p,MV_INTERNAL);you.turn_is_over=false;move_player_action(d);corner_allowed=you.pos()==n;corner_tested=1;
            }
        }
        if(walked>=5&&stopped>=5&&corner_tested)break;
    }
    for(rectangle_iterator it(1);it;++it){const auto door=*it;if(env.grid(door)!=DNGN_CLOSED_DOOR)continue;
        coord_def from;bool found=false;
        for(const auto &d:dirs)if(!d.x||!d.y){const auto p=door-d;
            if(in_bounds(p)&&env.grid(p)==DNGN_FLOOR){from=p;found=true;break;}}
        check(found,"107 door has no reachable approach");
        const auto delta=door-from;const auto behind=door+delta;
        const bool straight=in_bounds(behind)&&env.grid(behind)==DNGN_FLOOR;
        if(straight){los_grid seen;losight(seen,from,opc_default,circle_def(7,C_SQUARE));check(!seen(behind-from),"107 closed door leaks direct LOS");frame(from,"door-closed");}
        you.move_to(from,MV_INTERNAL);you.turn_is_over=false;move_player_action(delta);
        check(env.grid(door)==DNGN_OPEN_DOOR&&you.pos()==from,"107 first move must open door without stepping");
        you.turn_is_over=false;move_player_action(delta);check(you.pos()==door,"107 second move did not enter opened door");
        if(straight){los_grid seen;losight(seen,from,opc_default,circle_def(7,C_SQUARE));check(seen(behind-from),"107 opened door still blocks direct LOS");frame(from,"door-open");++los_doors;}
        you.move_to(from,MV_INTERNAL);you.turn_is_over=false;close_door_action(delta);check(env.grid(door)==DNGN_CLOSED_DOOR,"107 native close command failed");++doors;
    }
    for(int y=0;y<GYM;++y)for(int x=0;x<GXM;++x)check(env.grid(coord_def(x,y))==original_terrain[y*GXM+x],"107 interaction did not restore native terrain");
    out<<"],\"walkableCells\":"<<pass_cells<<",\"blockedCells\":"<<blocked_cells
       <<",\"reachableCells\":"<<reachable.size()<<",\"walkCommands\":"<<walked
       <<",\"blockedCommands\":"<<stopped<<",\"doorCommands\":"<<doors
       <<",\"doorLosPairs\":"<<los_doors<<",\"diagonalCornerTested\":"<<corner_tested
       <<",\"diagonalCornerAllowed\":"<<corner_allowed;
    // Controlled, real native placement for layering review only. This branch
    // is absent in normal city generation and is not an enemy/reward design.
    if(std::getenv("HOLOCRAWL_FACILITY107")){
        std::vector<coord_def> spots;
        const auto &f=facilities[selected];
        for(int y=1;y<f.height-1;++y)for(int x=1;x<f.width-1;++x){const auto p=origin+coord_def(x,y);if(env.grid(p)==DNGN_FLOOR)spots.push_back(p);}
        check(spots.size()>=3,"107 actor overlap scene needs3 walkable cells");
        you.move_to(spots[0],MV_INTERNAL);
        monster *mon=mons_place(mgen_data(MONS_ORC,BEH_HOSTILE,spots[1],MHITNOT,MG_FORCE_PLACE|MG_FORBID_BANDS));
        check(mon&&mon->pos()==spots[1],"107 native monster placement failed");
        int item=get_mitm_slot();check(item!=NON_ITEM,"107 no test item slot");
        env.item[item].base_type=OBJ_POTIONS;env.item[item].sub_type=POT_CURING;env.item[item].quantity=1;
        check(move_item_to_grid(&item,spots[2],true),"107 native item placement failed");
        const auto write_tile=[&](tileidx_t tile){
            tile&=TILE_FLAG_MASK;const bool player=tile>=TILE_MAIN_MAX;
            const auto &info=player?tile_player_info(tile):tile_main_info(tile);
            out<<"{\"atlas\":\""<<(player?"player":"main")<<"\",\"sx\":"<<info.sx<<",\"sy\":"<<info.sy
               <<",\"width\":"<<info.ex-info.sx<<",\"height\":"<<info.ey-info.sy<<",\"dx\":"<<int(info.offset_x)<<",\"dy\":"<<int(info.offset_y)<<'}';
        };
        out<<",\"actors\":[{\"kind\":\"player\",\"x\":"<<spots[0].x<<",\"y\":"<<spots[0].y<<",\"tiles\":[";
        dolls_data doll;for(int i=0;i<TILEP_PART_MAX;++i)doll.parts[i]=TILEP_SHOW_EQUIP;tilep_race_default(you.species,you.experience_level,&doll);tilep_job_default(you.char_class,&doll);
        check(doll.parts[TILEP_PART_BASE]>=TILE_MAIN_MAX&&doll.parts[TILEP_PART_BASE]<TILEP_PLAYER_MAX,"107 player base missing");
        int order[TILEP_PART_MAX],flags[TILEP_PART_MAX];tilep_fill_order_and_flags(doll,order,flags);bool first_part=true;
        for(int i=0;i<TILEP_PART_MAX;++i){const auto t=doll.parts[order[i]];
            if(t>=TILE_MAIN_MAX&&t<TILEP_PLAYER_MAX){if(!first_part)out<<',';first_part=false;write_tile(t);}}
        out<<"]},{\"kind\":\"monster\",\"x\":"<<spots[1].x<<",\"y\":"<<spots[1].y<<",\"tiles\":[";
        write_tile(tileidx_monster(monster_info(mon)));out<<"]},{\"kind\":\"item\",\"x\":"<<spots[2].x<<",\"y\":"<<spots[2].y<<",\"tiles\":[";
        write_tile(tileidx_item(env.item[item]));out<<"]}]";
    }
    out<<",\"status\":\"passed\"}";
    std::ofstream file(directory+"/probe-"+std::to_string(seed)+"-"+std::to_string(depth)+".json");
    check(bool(file),"107 cannot write native probe");file<<out.str()<<'\n';
    you.turn_is_over=false;you.move_to(saved_pos,MV_INTERNAL);
}
