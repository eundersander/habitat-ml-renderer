# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mochi
import os

def add_prefab(prefab_filepath, scene):

    # todo: clean up hard-coded path
    mochi_assets_root = "data/mochi_vr_data/mochi_assets_root"
    prefab = mochi.prefab.load_from_file(
        os.path.join(
            mochi_assets_root,
            prefab_filepath,
        ),
        mochi_assets_root,
    )

    params = mochi.prefab.CreatePrefabParams()
    mochi.prefab.add_to_scene(prefab, params, scene)
