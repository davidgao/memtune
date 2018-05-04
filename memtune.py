#!/usr/bin/env python3

import os

ksm_root = "/sys/kernel/mm/ksm/"

config_keys = [
    "max_page_sharing",
    "merge_across_nodes",
    "pages_to_scan",
    "run",
    "sleep_millisecs",
    "stable_node_chains_prune_millisecs",
    "use_zero_pages"
]

stat_keys = [
    "full_scans",
    "pages_shared",
    "pages_sharing",
    "pages_unshared",
    "pages_volatile",
    "stable_node_chains",
    "stable_node_dups"
]

perf_keys = dict({
    "save": "{}",
    "share_rate": "{:.2F}",
    "efficiency": "{:.1%}"
})

kv = dict()

# read
try:
    keys = os.listdir(ksm_root)
    for key in keys:
        with open(ksm_root + key) as f:
            val = f.read().split('\n')
            val.remove('')
            if len(val) == 1:
                val = val[0]
                if val.isdecimal():
                    val = int(val)
        kv[key] = val
except OSError:
    print("OSError")

# calculate performance
try:
    shared = kv["pages_shared"]
    sharing = kv["pages_sharing"]
    unshared = kv["pages_unshared"]
    all = shared + sharing + unshared

    # save
    save = sharing * 4
    suffix = 'K'
    if save > 1024:
        save /= 1024
        suffix = 'M'
    if save > 1024:
        save /= 1024
        suffix = 'G'
    kv["save"] = "{:.1F}{}".format(save, suffix)

    # share rate
    if shared > 0:
        kv["share_rate"] = sharing / shared + 1.0
    else:
        kv["share_rate"] = 1.0

    # efficiency
    if all > 0:
        kv["efficiency"] = shared / all
    else:
        kv["efficiency"] = 1.0
except:
    print("Exception during performance calculation")

# print
print("Config:")
for key in config_keys:
    if key in kv:
        print("{:20}: {}".format(key, kv[key]))
        kv.pop(key)

print()
print("Statistics:")
for key in stat_keys:
    if key in kv:
        print("{:20}: {}".format(key, kv[key]))
        kv.pop(key)

print()
print("Performance:")
for key in perf_keys:
    if key in kv:
        print(("{:20}: " + perf_keys[key]).format(key, kv[key]))
        kv.pop(key)
