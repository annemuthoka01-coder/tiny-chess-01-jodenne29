import json, os, sys, random, urllib.request
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

KN, KG, RAYS = [], [], {}
for sq in range(64):
    r, c = sq // 8, sq % 8
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

def parse_fen(f):
    p = f.split(); b = ['.'] * 64
    for r, w in enumerate(p[0].split('/')):
        c = 0
        for ch in w:
            if ch.isdigit(): c += int(ch)
            else: b[r * 8 + c] = ch; c += 1
    ep = p[3]
    ep_idx = ord(ep[0]) - ord('a') + (8 - int(ep[1])) * 8 if ep != '-' else -1
    h = 0
    for sq, ch in enumerate(b):
        if ch != '.': h ^= Z_PIECE[ch][sq]
    if p[1] == 'w': h ^= Z_SIDE
    return [b, p[1], p[2], ep_idx, h]

fs = lambda s: s % 8
rs = lambda s: s // 8
uc = lambda m: "abcdefgh"[m[1]] + str(8 - m[0]) + "abcdefgh"[m[3]] + str(8 - m[2]) + m[4]

def ia(b, s, bw):
    for ts in KN[s]:
        if b[ts] == ('N' if bw else 'n'): return 1
    for ts in KG[s]:
        if b[ts] == ('K' if bw else 'k'): return 1
    pwns = [s + 7, s + 9] if bw else [s - 9, s - 7]
    for ts in pwns:
        if 0 <= ts < 64 and abs(fs(s) - fs(ts)) == 1:
            if b[ts] == ('P' if bw else 'p'): return 1
    for i, ray in enumerate(RAYS[s]):
        pc = 'RQ' if i < 4 else 'BQ'
        target = pc if bw else pc.lower()
        for ts in ray:
            p = b[ts]
            if p != '.':
                if p in target: return 1
                break
    return 0

def gm(P):
    b, t, c, e, _ = P; w = (t == 'w'); m = []
    for sq in range(64):
        p = b[sq]
        if p == '.' or (p.isupper() != w): continue
        fr, fc = rs(sq), fs(sq); pt = p.lower()
        if pt == 'p':
            dr = -1 if w else 1; sr = 6 if w else 1; ts = sq + dr * 8
            if 0 <= ts < 64 and b[ts] == '.':
                if rs(ts) == (0 if w else 7):
                    for q in 'qrbn': m.append((fr, fc, rs(ts), fs(ts), q))
                else: m.append((fr, fc, rs(ts), fs(ts), ''))
                if fr == sr and b[sq + dr * 16] == '.': m.append((fr, fc, rs(sq + dr * 16), fs(sq + dr * 16), ''))
            for dc in (-1, 1):
                nc = fc + dc
                if 0 <= nc < 8:
                    ts = sq + dr * 8 + dc
                    if 0 <= ts < 64:
                        tp = b[ts]
                        if (tp != '.' and (tp.isupper() != w)) or ts == e:
                            if rs(ts) == (0 if w else 7):
                                for q in 'qrbn': m.append((fr, fc, rs(ts), fs(ts), q))
                            else: m.append((fr, fc, rs(ts), fs(ts), ''))
        elif pt in 'nk':
            for ts in (KN[sq] if pt == 'n' else KG[sq]):
                tp = b[ts]
                if tp == '.' or (tp.isupper() != w): m.append((fr, fc, rs(ts), fs(ts), ''))
        else:
            ranges = range(4) if pt == 'r' else (range(4, 8) if pt == 'b' else range(8))
            for ri in ranges:
                for ts in RAYS[sq][ri]:
                    tp = b[ts]
                    if tp == '.' or (tp.isupper() != w): m.append((fr, fc, rs(ts), fs(ts), ''))
                    if tp != '.': break
    if w:
        if 'K' in c and b[61] == '.' and b[62] == '.' and not ia(b, 60, 0) and not ia(b, 61, 0) and not ia(b, 62, 0): m.append((7, 4, 7, 6, ''))
        if 'Q' in c and b[59] == '.' and b[58] == '.' and b[57] == '.' and not ia(b, 60, 0) and not ia(b, 59, 0) and not ia(b, 58, 0): m.append((7, 4, 7, 2, ''))
    else:
        if 'k' in c and b[5] == '.' and b[6] == '.' and not ia(b, 4, 1) and not ia(b, 5, 1) and not ia(b, 6, 1): m.append((0, 4, 0, 6, ''))
        if 'q' in c and b[3] == '.' and b[2] == '.' and b[1] == '.' and not ia(b, 4, 1) and not ia(b, 3, 1) and not ia(b, 2, 1): m.append((0, 4, 0, 2, ''))
    lg = []
    kch = 'K' if w else 'k'
    for mv in m:
        u = mk(P, mv)
        ksq = -1
        for sq_i, p_i in enumerate(P[0]):
            if p_i == kch: ksq = sq_i; break
        if ksq == -1 or not ia(P[0], ksq, not w):
            lg.append(mv)
        um(P, mv, u)
    return lg

def mk(P, m):
    b, t, c, e, h = P; old_h = h; fr1, fc1, fr2, fc2, q = m; fs, ts = fr1 * 8 + fc1, fr2 * 8 + fc2; p = b[fs]; cap = b[ts]; nep = -1; cr = None; cs = -1
    h ^= Z_PIECE[p][fs]
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
    nc = c
    for ch, tk in [('K', 'KQ'), ('k', 'kq')]:
        if p == ch: nc = nc.replace(ch, '').replace(tk[1], '')
    if fs == 0 or ts == 0: nc = nc.replace('q', '')
    if fs == 7 or ts == 7: nc = nc.replace('k', '')
    if fs == 56 or ts == 56: nc = nc.replace('Q', '')
    if fs == 63 or ts == 63: nc = nc.replace('K', '')
    if nc == '': nc = '-'
    h ^= Z_SIDE
    P[1] = 'b' if t == 'w' else 'w'; P[2] = nc; P[3] = nep; P[4] = h
    return (p, cap, c, e, cr, fs, ts, cs, old_h)

def um(P, m, u):
    orig_p, cap, oc, oep, cr, fs, ts, cs, oh = u; b, t, _, _, _ = P
    P[1] = 'w' if t == 'b' else 'b'; P[2] = oc; P[3] = oep; P[4] = oh
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
    b, t, _, _, _ = P; w = (t == 'w')
    score = 0; w_bc = 0; b_bc = 0
    for sq, p in enumerate(b):
        if p == '.': continue
        pt = p.lower(); is_w = p.isupper()
        val = PV[pt] + PST[pt][sq if is_w else (sq ^ 56)]
        if pt == 'b':
            if is_w: w_bc += 1
            else: b_bc += 1
        if is_w: score += val
        else: score -= val
    if w_bc >= 2: score += 30
    if b_bc >= 2: score -= 30
    return score if w else -score

TT = {}
NODES = 0

def quiescence(P, alpha, beta, ply):
    global NODES; NODES += 1
    stand = evaluate(P)
    if stand >= beta: return beta
    if alpha < stand: alpha = stand
    b, t, _, _, _ = P; w = (t == 'w')
    kch = 'K' if w else 'k'
    ksq = -1
    for sq_i, p_i in enumerate(b):
        if p_i == kch: ksq = sq_i; break
    in_chk = ia(b, ksq, not w) if ksq != -1 else False
    mvs = gm(P)
    legal = mvs if in_chk else [m for m in mvs if b[m[2]*8+m[3]] != '.' or m[4] != '']
    for m in legal:
        u = mk(P, m)
        score = -quiescence(P, -beta, -alpha, ply + 1)
        um(P, m, u)
        if score >= beta: return beta
        if score > alpha: alpha = score
    return alpha

def alphabeta(P, depth, alpha, beta, ply):
    global NODES; NODES += 1
    if depth <= 0: return quiescence(P, alpha, beta, ply)
    h = P[4]; key = (h, P[1], P[2], P[3])
    if key in TT:
        d_tt, v_tt, flag_tt, _ = TT[key]
        if d_tt >= depth:
            if flag_tt == 0: return v_tt
            if flag_tt == 1 and v_tt <= alpha: return alpha
            if flag_tt == 2 and v_tt >= beta: return beta
    mvs = gm(P)
    b, t, _, _, _ = P; w = (t == 'w')
    if not mvs:
        kch = 'K' if w else 'k'
        ksq = -1
        for sq_i, p_i in enumerate(b):
            if p_i == kch: ksq = sq_i; break
        if ksq != -1 and ia(b, ksq, not w): return -100000 + ply
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
        if val > best_val: best_val = val; bm = m
        if val > alpha: alpha = val
        if alpha >= beta: flag = 2; break
    if best_val <= orig_a: flag = 1
    TT[key] = (depth, best_val, flag, bm)
    return best_val

def best_move(fen, legal):
    global NODES, TT; NODES = 0; TT.clear()
    pos = parse_fen(fen)
    best_m = None
    for d in range(1, 10):
        if NODES > 85000: break
        alpha = -1000000; beta = 1000000
        mvs = gm(pos)
        b, t, _, _, _ = pos
        def score_m(m):
            h = pos[4]; key = (h, pos[1], pos[2], pos[3])
            if key in TT and TT[key][3] == m: return 10000
            target = b[m[2]*8+m[3]]
            if target != '.': return 1000 + PV[target.lower()]
            if m[4]: return 900
            return 0
        mvs.sort(key=score_m, reverse=True)
        bv = -1000000; bm = None
        for m in mvs:
            u = mk(pos, m)
            val = -alphabeta(pos, d - 1, -beta, -alpha, d)
            um(pos, m, u)
            if val > bv: bv = val; bm = m
            if val > alpha: alpha = val
        if bm: best_m = bm
        if NODES > 85000: break
    return uc(best_m) if best_m else (uc(gm(pos)[0]) if gm(pos) else "")

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
