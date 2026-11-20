"""Street-facing bays of the north islet and the market east of the ditch."""
from .landscape import poly
from .street_houses import along, stroke


MARKETS = {
    'islet': ('wood-560', ('wood-560','wood-561','wood-563','wood-566','wood-564','wood-567'), (
        ('islet-back', (664.1,743.8), (682.4,738.55), (664.6,749.85), (682.9,745.1), (0,.28,.52,.78,1), 'upper'),
        ('islet-middle', (667.2,755.75), (684.35,752.15), (667.35,761.0), (684.6,757.65), (0,.30,.57,.79,1), 'single'),
        ('islet-street', (654.15,769.7), (690.2,761.7), (654.4,775.85), (690.45,767.35), (0,.13,.26,.40,.55,.69,.84,1), 'street'),
        ('islet-kiosk-back', (692.8,737.25), (706.4,735.65), (693.05,743.25), (706.6,741.65), (0,.46,.74,1), 'single'),
        ('islet-kiosk-front', (695.0,752.35), (708.7,751.65), (695.1,758.05), (708.75,756.8), (0,.30,.61,1), 'single'),
    )),
    'ditch': ('wood-599', ('wood-599','wood-587'), (
        ('ditch-back-shop', (521.15,662.75), (532.7,662.1), (521.0,667.25), (533.1,667.45), (0,.38,.72,1), 'single'),
        ('ditch-street-loft', (520.15,673.05), (533.05,672.7), (520.45,684.0), (533.55,683.65), (0,.22,.52,.78,1), 'loft'),
    )),
}


def street_bays(name, left, right, foot_left, foot_right, columns, kind):
    def at(across, down):
        return along(along(left,right,across), along(foot_left,foot_right,across), down)
    def board(start, stop, head, sill, fill):
        return poly([at(start,head), at(stop,head), at(stop,sill), at(start,sill)], fill)
    pieces = [poly([left, right, foot_right, foot_left], '#755043')]
    levels = ((.12,.43),(.55,.95)) if kind == 'loft' else ((.17,.85),)
    for level, (head,sill) in enumerate(levels):
        for index,(start,stop) in enumerate(zip(columns,columns[1:])):
            margin = .075 * (stop-start)
            jamb, end = start+margin, stop-margin
            palette = ('#69483e','#584039','#795144') if kind in ('street','single') else ('#55433d','#6d4a3e','#5c413a')
            pieces.append(board(jamb,end,head,sill,palette[(index+level)%3]))
            mid = (start+stop)/2
            pieces.append(stroke([at(mid,head+.02),at(mid,sill)], '#4f3932', .27))
            if kind in ('upper','loft') and level == 0:
                pieces.append(stroke([at(jamb,.33),at(end,.33)], '#927664', .29))
    if kind == 'loft':
        pieces.append(board(0,1,.43,.54,'#4d3832'))
    for column in columns:
        pieces.append(stroke([at(column,.045),at(column,.99)], '#50392f', .72 if kind=='street' else .58))
    pieces.append(board(0,1,0,.135,'#493a34'))
    pieces.append(stroke([left,right],'#454047',.58))
    return f'<g id="nw-market-{name}" data-storeys="{2 if kind=="loft" else 1}">'+''.join(pieces)+'</g>'


def market_layer(surfaces):
    present = {feature['id'] for feature in surfaces}
    removed, fronts = set(), []
    for name, (anchor, timber, bays) in MARKETS.items():
        if anchor not in present:
            continue
        if not present.issuperset(timber):
            raise ValueError(f'Incomplete street timber sources for {name}')
        removed.update(timber)
        fronts.append(f'<g id="nw-market-{name}">'+''.join(street_bays(*bay) for bay in bays)+'</g>')
    return removed, ''.join(fronts)
