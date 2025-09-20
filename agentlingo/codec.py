import json, numpy as np, xxhash

def encode_latent(isr: dict):
    s = json.dumps(isr, sort_keys=True).encode()
    seed = xxhash.xxh64(s).intdigest()
    rng = np.random.default_rng(seed)
    vec8 = rng.normal(0,1,8); vec8 = (vec8 / (np.linalg.norm(vec8)+1e-9)).tolist()
    simhash64 = f"0x{seed:016x}"
    return {"vec8": vec8, "simhash64": simhash64}

_LATENT_INDEX = {}

def register_template(isr: dict):
    lat = encode_latent(isr)
    _LATENT_INDEX[lat["simhash64"]] = isr
    return lat

def decode_latent(lat: dict):
    return _LATENT_INDEX.get(lat.get("simhash64"))
