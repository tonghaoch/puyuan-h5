"""Schedule an existing courtyard directly behind its registered foreground house."""


def court_bindings(groups):
    sources = {}
    targets = {}
    for order, group in enumerate(groups):
        for field, objects, slots in [('courtLayers', 'courts', sources), ('courtBeforeHouse', 'houses', targets)]:
            for index, key in group.get(field, {}).items():
                if key in slots or not 0 <= int(index) < len(group[objects]):
                    raise ValueError(f'Invalid {field} binding {key} in {group["id"]}')
                if group.get('visibleOnly') or 'standaloneElevation' in group:
                    raise ValueError(f'Cannot move court across a locally clipped group: {key}')
                slots[key] = order
    if sources.keys() != targets.keys() or any(targets[key] >= order for key, order in sources.items()):
        raise ValueError('A moved courtyard needs one earlier foreground house')
