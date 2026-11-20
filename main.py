import json, os, sys, random, urllib.request, time
E = os.environ.get("MAKEFUN_ENV_URL")
PV = {'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 0}
_PST_P = "@@@@@@@@HHHHHHHHJJJJJJJJLLLLLLLLNNNNNNNNPPPPPPPPSSSSSSSS@@@@@@@@"
_PST_N = "(((((())++,,,-..122333221100/-,,+**)(())((()))))((((((()))))(((("
_PST_B = ")),,-..0122210/-,,++*())(((())((()))))(((()***++,,,/0122210/,-,)"
_PST_R = "))))))))...12343210..............012343210))))))))))))))))))))))"
_PST_Q = ")))))))))...12343210.............012343210))))))))))))))))))))))"
_PST_K = "ZZZZZZZZYYYYYYYYWWWWWWWWUUUUUUUURRRRRRRRKKKKKKKK@@@@@@@@@@@@@@@@"
_dec = lambda s: [ord(c) - 64 for c in s]
PST = {'p': _dec(_PST_P), 'n': _dec(_PST_N), 'b': _dec(_PST_B), 'r': _dec(_PST_R), 'q': _dec(_PST_Q), 'k': _dec(_PST_K)}

EVAL_TABLE = {}
for ch in 'pnbrqkPNBRQK':
    is_w = ch.isupper(); pt = ch.lower()
    mat = PV[pt]
    tbl = []
    for sq in range(64):
        pst_sq = sq if is_w else (sq ^ 56)
        val = mat + PST[pt][pst_sq]
        tbl.append(val if is_w else -val)
    EVAL_TABLE[ch] = tbl

SQ_FILE = [sq % 8 for sq in range(64)]
SQ_RANK = [sq // 8 for sq in range(64)]

KN, KG, RAYS = [], [], {}
for sq in range(64):
    r, c = SQ_RANK[sq], SQ_FILE[sq]
    kn = []
    for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8: kn.append(nr * 8 + nc)
    KN.append(kn)
    kg = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8: kg.append(nr * 8 + nc)
    KG.append(kg)
    rays = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
        ray = []
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            ray.append(nr * 8 + nc)
            nr, nc = nr + dr, nc + dc
        rays.append(ray)
    RAYS[sq] = rays

rnd = random.Random(12345)
Z_PIECE = {p: [rnd.getrandbits(64) for _ in range(64)] for p in 'pnbrqkPNBRQK'}
Z_SIDE = rnd.getrandbits(64)
Z_CASTLE = {c: rnd.getrandbits(64) for c in ['K', 'Q', 'k', 'q']}
Z_EP = {f: rnd.getrandbits(64) for f in range(8)}

def parse_fen(f):
    p = f.split(); b = ['.'] * 64
    wk_sq = eb_sq = -1
    for r, w in enumerate(p[0].split('/')):
        c = 0
        for ch in w:
            if ch.isdigit(): c += int(ch)
            else:
                sq = r * 8 + c
                b[sq] = ch
                if ch == 'K': wk_sq = sq
                elif ch == 'k': eb_sq = sq
                c += 1
    ep = p[3]
    ep_idx = ord(ep[0]) - ord('a') + (8 - int(ep[1])) * 8 if ep != '-' else -1
    h = 0
    for sq, ch in enumerate(b):
        if ch != '.': h ^= Z_PIECE[ch][sq]
    if p[1] == 'w': h ^= Z_SIDE
    for cr_ch in p[2]:
        if cr_ch in Z_CASTLE: h ^= Z_CASTLE[cr_ch]
    if ep_idx != -1:
        h ^= Z_EP[ep_idx % 8]
    return [b, p[1], p[2], ep_idx, h, wk_sq, eb_sq]

uc = lambda m: "abcdefgh"[m[1]] + str(8 - m[0]) + "abcdefgh"[m[3]] + str(8 - m[2]) + m[4]

def ia(b, s, bw):
    if s == -1 or s not in range(64): return 0
    f_s = SQ_FILE[s]
    for ts in KN[s]:
        if b[ts] == ('N' if bw else 'n'): return 1
    for ts in KG[s]:
        if b[ts] == ('K' if bw else 'k'): return 1
    pwns = [s + 7, s + 9] if bw else [s - 9, s - 7]
    for ts in pwns:
        if 0 <= ts < 64 and abs(f_s - SQ_FILE[ts]) == 1:
            if b[ts] == ('P' if bw else 'p'): return 1
    for i, ray in enumerate(RAYS[s]):
        target = ('RQ' if i < 4 else 'BQ') if bw else ('rq' if i < 4 else 'bq')
        for ts in ray:
            p = b[ts]
            if p != '.':
                if p in target: return 1
                break
    return 0

def filter_legal(P, m, w, ksq):
    b, _, _, e, _, _, _ = P
    in_check = ia(b, ksq, not w) if (ksq != -1 and ksq in range(64)) else True
    if in_check:
        lg = []
        for mv in m:
            u = mk(P, mv)
            curr_ksq = P[5] if w else P[6]
            if curr_ksq == -1 or curr_ksq not in range(64):
                try: curr_ksq = P[0].index('K' if w else 'k')
                except ValueError: curr_ksq = 0
            if not ia(P[0], curr_ksq, not w):
                lg.append(mv)
            um(P, mv, u)
        return lg
    else:
        blockers = set()
        for ray in RAYS[ksq]:
            for ts in ray:
                p = b[ts]
                if p != '.':
                    if p.isupper() == w:
                        blockers.add(ts)
                    break
        lg = []
        for mv in m:
            fr1, fc1, fr2, fc2, q = mv
            fs = fr1 * 8 + fc1
            ts = fr2 * 8 + fc2
            p = b[fs]
            if p.lower() == 'k' or ts == e or fs in blockers:
                u = mk(P, mv)
                curr_ksq = P[5] if w else P[6]
                if curr_ksq == -1 or curr_ksq not in range(64):
                    try: curr_ksq = P[0].index('K' if w else 'k')
                    except ValueError: curr_ksq = 0
                if not ia(P[0], curr_ksq, not w):
                    lg.append(mv)
                um(P, mv, u)
            else:
                lg.append(mv)
        return lg

def gm(P):
    b, t, c, e, _, wk, eb = P; w = (t == 'w'); m = []
    ksq = wk if w else eb
    if ksq == -1 or ksq not in range(64):
        try: ksq = P[0].index('K' if w else 'k')
        except ValueError: ksq = 0

    for sq in range(64):
        p = b[sq]
        if p == '.' or (p.isupper() != w): continue
        fr, fc = SQ_RANK[sq], SQ_FILE[sq]; pt = p.lower()
        if pt == 'p':
            dr = -1 if w else 1; sr = 6 if w else 1; ts = sq + dr * 8
            if 0 <= ts < 64 and b[ts] == '.':
                if SQ_RANK[ts] == (0 if w else 7):
                    for q in 'qrbn': m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], q))
                else: m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
                if fr == sr and b[sq + dr * 16] == '.': m.append((fr, fc, SQ_RANK[sq + dr * 16], SQ_FILE[sq + dr * 16], ''))
            for dc in (-1, 1):
                nc = fc + dc
                if 0 <= nc < 8:
                    ts = sq + dr * 8 + dc
                    if 0 <= ts < 64:
                        tp = b[ts]
                        if (tp != '.' and (tp.isupper() != w)) or ts == e:
                            if SQ_RANK[ts] == (0 if w else 7):
                                for q in 'qrbn': m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], q))
                            else: m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
        elif pt in 'nk':
            for ts in (KN[sq] if pt == 'n' else KG[sq]):
                tp = b[ts]
                if tp == '.' or (tp.isupper() != w): m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
        else:
            ranges = range(4) if pt == 'r' else (range(4, 8) if pt == 'b' else range(8))
            for ri in ranges:
                for ts in RAYS[sq][ri]:
                    tp = b[ts]
                    if tp == '.' or (tp.isupper() != w): m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
                    if tp != '.': break
    if w:
        if 'K' in c and b[61] == '.' and b[62] == '.' and not ia(b, 60, 0) and not ia(b, 61, 0) and not ia(b, 62, 0): m.append((7, 4, 7, 6, ''))
        if 'Q' in c and b[59] == '.' and b[58] == '.' and b[57] == '.' and not ia(b, 60, 0) and not ia(b, 59, 0) and not ia(b, 58, 0): m.append((7, 4, 7, 2, ''))
    else:
        if 'k' in c and b[5] == '.' and b[6] == '.' and not ia(b, 4, 1) and not ia(b, 5, 1) and not ia(b, 6, 1): m.append((0, 4, 0, 6, ''))
        if 'q' in c and b[3] == '.' and b[2] == '.' and b[1] == '.' and not ia(b, 4, 1) and not ia(b, 3, 1) and not ia(b, 2, 1): m.append((0, 4, 0, 2, ''))
    
    return filter_legal(P, m, w, ksq)

def gm_caps(P):
    b, t, c, e, _, wk, eb = P; w = (t == 'w'); m = []
    ksq = wk if w else eb
    if ksq == -1 or ksq not in range(64):
        try: ksq = P[0].index('K' if w else 'k')
        except ValueError: ksq = 0

    for sq in range(64):
        p = b[sq]
        if p == '.' or (p.isupper() != w): continue
        fr, fc = SQ_RANK[sq], SQ_FILE[sq]; pt = p.lower()
        if pt == 'p':
            dr = -1 if w else 1; ts = sq + dr * 8
            if 0 <= ts < 64 and b[ts] == '.':
                if SQ_RANK[ts] == (0 if w else 7):
                    for q in 'qrbn': m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], q))
            for dc in (-1, 1):
                nc = fc + dc
                if 0 <= nc < 8:
                    ts = sq + dr * 8 + dc
                    if 0 <= ts < 64:
                        tp = b[ts]
                        if (tp != '.' and (tp.isupper() != w)) or ts == e:
                            if SQ_RANK[ts] == (0 if w else 7):
                                for q in 'qrbn': m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], q))
                            else: m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
        elif pt in 'nk':
            for ts in (KN[sq] if pt == 'n' else KG[sq]):
                tp = b[ts]
                if tp != '.' and (tp.isupper() != w): m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
        else:
            ranges = range(4) if pt == 'r' else (range(4, 8) if pt == 'b' else range(8))
            for ri in ranges:
                for ts in RAYS[sq][ri]:
                    tp = b[ts]
                    if tp != '.':
                        if tp.isupper() != w: m.append((fr, fc, SQ_RANK[ts], SQ_FILE[ts], ''))
                        break
    return filter_legal(P, m, w, ksq)
def mk(P, m):
    b, t, c, e, h, wk, eb = P; old_h = h; old_wk = wk; old_eb = eb; old_c = c; old_e = e
    fr1, fc1, fr2, fc2, q = m; fs, ts = fr1 * 8 + fc1, fr2 * 8 + fc2; p = b[fs]; cap = b[ts]; nep = -1; cr = None; cs = -1
    h ^= Z_PIECE[p][fs]
    if e != -1: h ^= Z_EP[e % 8]
    if p.lower() == 'p' and ts == e:
        cs = ts + (8 if t == 'w' else -8); cap = b[cs]; b[cs] = '.'; h ^= Z_PIECE['p' if t == 'w' else 'P'][cs]
    if p.lower() == 'p' and abs(fr2 - fr1) == 2: nep = (fs + ts) // 2
    if p.lower() == 'k' and abs(fc2 - fc1) == 2:
        if fc2 == 6:
            cr = (fs + 3, fs + 1, b[fs+3]); b[fs + 1] = b[fs + 3]; b[fs + 3] = '.'
            h ^= Z_PIECE['R' if t == 'w' else 'r'][fs+3] ^ Z_PIECE['R' if t == 'w' else 'r'][fs+1]
        elif fc2 == 2:
            cr = (fs - 4, fs - 1, b[fs-4]); b[fs - 1] = b[fs - 4]; b[fs - 4] = '.'
            h ^= Z_PIECE['R' if t == 'w' else 'r'][fs-4] ^ Z_PIECE['R' if t == 'w' else 'r'][fs-1]
    np_piece = (q.upper() if t == 'w' else q.lower()) if q else p
    b[ts] = np_piece; b[fs] = '.'
    h ^= Z_PIECE[np_piece][ts]
    if cap != '.' and not (p.lower() == 'p' and ts == e):
        h ^= Z_PIECE[cap][ts]
    if p == 'K': wk = ts
    elif p == 'k': eb = ts
    nc = c
    if p == 'K': nc = nc.replace('K', '').replace('Q', '')
    elif p == 'k': nc = nc.replace('k', '').replace('q', '')
    if fs == 56 or ts == 56: nc = nc.replace('Q', '')
    if fs == 63 or ts == 63: nc = nc.replace('K', '')
    if fs == 0 or ts == 0: nc = nc.replace('q', '')
    if fs == 7 or ts == 7: nc = nc.replace('k', '')
    if nc == '': nc = '-'
    for ch_c in c:
        if ch_c not in nc: h ^= Z_CASTLE[ch_c]
    h ^= Z_SIDE
    if nep != -1: h ^= Z_EP[nep % 8]
    P[1] = 'b' if t == 'w' else 'w'; P[2] = nc; P[3] = nep; P[4] = h; P[5] = wk; P[6] = eb
    return (p, cap, old_c, old_e, cr, fs, ts, cs, old_h, old_wk, old_eb)

def um(P, m, u):
    orig_p, cap, oc, oep, cr, fs, ts, cs, oh, owk, oeb = u; b, t, _, _, _, _, _ = P
    P[1] = 'w' if t == 'b' else 'b'; P[2] = oc; P[3] = oep; P[4] = oh; P[5] = owk; P[6] = oeb
    if cr:
        rf, rt, rp = cr; b[rf] = rp; b[rt] = '.'
    if cs != -1:
        b[cs] = 'p' if t == 'b' else 'P'
        b[ts] = '.'
    else:
        b[ts] = cap
    b[fs] = orig_p

def perft(P, d):
    if d == 0: return 1
    mvs = gm(P)
    if d == 1: return len(mvs)
    cnt = 0
    for m in mvs:
        u = mk(P, m)
        cnt += perft(P, d - 1)
        um(P, m, u)
    return cnt

def evaluate(P):
    b, t, _, _, _, _, _ = P; w = (t == 'w')
    score = 0; w_bc = 0; b_bc = 0
    for sq, p in enumerate(b):
        if p == '.': continue
        score += EVAL_TABLE[p][sq]
        if p == 'B': w_bc += 1
        elif p == 'b': b_bc += 1
    if w_bc >= 2: score += 30
    if b_bc >= 2: score -= 30
    return score if w else -score

TT = {}
NODES = 0
MAX_NODES = 0

def quiescence(P, alpha, beta, ply):
    global NODES
    NODES += 1
    if NODES >= MAX_NODES: return alpha
    stand = evaluate(P)
    if stand >= beta: return beta
    if alpha < stand: alpha = stand
    b, t, _, _, _, wk, eb = P; w = (t == 'w')
    ksq = wk if w else eb
    if ksq == -1 or ksq not in range(64):
        try: ksq = P[0].index('K' if w else 'k')
        except ValueError: ksq = 0
    in_chk = ia(b, ksq, not w)
    legal = gm(P) if in_chk else gm_caps(P)
    for m in legal:
        u = mk(P, m)
        score = -quiescence(P, -beta, -alpha, ply + 1)
        um(P, m, u)
        if NODES >= MAX_NODES: return alpha
        if score >= beta: return beta
        if score > alpha: alpha = score
    return alpha
def alphabeta(P, depth, alpha, beta, ply):
    global NODES
    NODES += 1
    if NODES >= MAX_NODES: return alpha
    if depth <= 0: return quiescence(P, alpha, beta, ply)
    h = P[4]; key = h
    if key in TT:
        d_tt, v_tt, flag_tt, _ = TT[key]
        if d_tt >= depth:
            if flag_tt == 0: return v_tt
            if flag_tt == 1 and v_tt <= alpha: return alpha
            if flag_tt == 2 and v_tt >= beta: return beta
    mvs = gm(P)
    b, t, _, _, _, wk, eb = P; w = (t == 'w')
    if not mvs:
        ksq = wk if w else eb
        if ksq == -1 or ksq not in range(64):
            try: ksq = P[0].index('K' if w else 'k')
            except ValueError: ksq = 0
        if ia(b, ksq, not w): return -100000 + ply
        return 0
    def score_m(m):
        if key in TT and TT[key][3] == m: return 10000
        target = b[m[2]*8+m[3]]
        if target != '.': return 1000 + PV[target.lower()] - PV[b[m[0]*8+m[1]].lower()] // 10
        if m[4]: return 900
        return 0
    mvs.sort(key=score_m, reverse=True)
    best_val = -1000000; bm = None; orig_a = alpha; flag = 0
    for m in mvs:
        u = mk(P, m)
        val = -alphabeta(P, depth - 1, -beta, -alpha, ply + 1)
        um(P, m, u)
        if NODES >= MAX_NODES: return alpha
        if val > best_val: best_val = val; bm = m
        if val > alpha: alpha = val
        if alpha >= beta: flag = 2; break
    if best_val <= orig_a: flag = 1
    TT[key] = (depth, best_val, flag, bm)
    return best_val

def best_move(fen, legal):
    global NODES, TT, MAX_NODES; NODES = 0; TT.clear()
    MAX_NODES = 40000
    pos = parse_fen(fen)
    best_m = legal[0] if legal else ""
    for d in range(1, 10):
        if NODES >= MAX_NODES: break
        alpha = -1000000; beta = 1000000
        mvs = gm(pos)
        b, t, _, _, _, _, _ = pos
        def score_m(m):
            h = pos[4]; key = h
            if key in TT and TT[key][3] == m: return 10000
            target = b[m[2]*8+m[3]]
            if target != '.': return 1000 + PV[target.lower()]
            if m[4]: return 900
            return 0
        mvs.sort(key=score_m, reverse=True)
        bv = -1000000; bm = None; iteration_failed = False
        for m in mvs:
            u = mk(pos, m)
            val = -alphabeta(pos, d - 1, -beta, -alpha, d)
            um(pos, m, u)
            if NODES >= MAX_NODES:
                iteration_failed = True
                break
            if val > bv: bv = val; bm = m
            if val > alpha: alpha = val
        if iteration_failed:
            break
        if bm: best_m = bm
        if NODES >= MAX_NODES: break
    bm_str = uc(best_m) if best_m and not isinstance(best_m, str) else best_m
    if bm_str in legal: return bm_str
    for lm in legal:
        if lm[:4] == bm_str[:4]: return lm
    return legal[0] if legal else ""

if __name__ == '__main__':
    def post(path, body):
        req = urllib.request.Request(E + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
        with urllib.request.urlopen(req) as res: return json.load(res)
    while True:
        g = post("/game", {})
        if g["status"] == "done": break
        while g["status"] == "your_move":
            m = best_move(g["fen"], g["legal_moves"])
            g = post("/move", {"game": g["game"], "move": m})
        print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
    print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost", file=sys.stderr)
