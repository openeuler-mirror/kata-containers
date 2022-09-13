#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
# Description: This script uses to update docker-ce component's version and release
# Create: 2022-09-12

old_version=`head -n 5 kata-containers.spec|grep RELEASE|awk '{print $NF}'`
let new_version=$old_version+1
sed -i -e "s/RELEASE $old_version/RELEASE $new_version/g" ./kata-containers.spec

author=$(git config user.name)
email=$(git config user.email)
version=$(head -5 kata-containers.spec | grep VERSION | awk '{print $NF}')
release=$(head -5 kata-containers.spec | grep RELEASE | awk '{print $NF}')
new_all=$version-$release
new_changelog=$(cat << EOF
* $(LC_ALL="C" date '+%a %b %d %Y') $author<$email> - $new_all\n- Type:\n- CVE:\n- SUG:\n- DESC:\n
EOF
)
sed -i -e "/\%changelog/a$new_changelog" kata-containers.spec
