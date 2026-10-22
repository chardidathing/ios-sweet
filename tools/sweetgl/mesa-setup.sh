#!/bin/sh
# after ios-sailfish by joranv1, ported to the xperia 1 ii (pdx203)
# configure mesa (MESA_SRC, with tools/sweetgl/mesa.patch applied) for ios 16
# arm64 into MESA_BUILD: gallium freedreno + gles, no window system, no llvm.
# needs a mac with xcode (xcrun), meson, ninja, bison > 2.3, flex and a
# python3 that imports mako and yaml.
#   MESA_SRC=research/mesa MESA_BUILD=research/mesa-ios tools/sweetgl/mesa-setup.sh [meson args]
set -e
H=$(cd "$(dirname "$0")" && pwd)
R=$(cd "$H/../.." && pwd)
M=$(cd "${MESA_SRC:-$R/research/mesa}" && pwd)
B=${MESA_BUILD:-$R/research/mesa-ios}
SDK=$(xcrun --sdk iphoneos --show-sdk-path)
CROSS=$B.cross.txt
mkdir -p "$(dirname "$B")"
# meson wants literal paths in the cross file, so fill the template per machine
sed -e "s|@CLANG@|$(xcrun --sdk iphoneos --find clang)|g" \
	-e "s|@CLANGXX@|$(xcrun --sdk iphoneos --find clang++)|g" \
	-e "s|@AR@|$(xcrun --sdk iphoneos --find ar)|g" \
	-e "s|@STRIP@|$(xcrun --sdk iphoneos --find strip)|g" \
	-e "s|@SDK@|$SDK|g" -e "s|@INC@|$H/include|g" "$H/ios-cross.txt" > "$CROSS"
cd "$M"
rm -rf "$B"
meson setup "$B" --cross-file "$CROSS" \
	--buildtype=release -Db_ndebug=true -Ddefault_library=static \
	-Dplatforms= -Degl=disabled -Dglx=disabled -Dgbm=disabled \
	-Dgallium-drivers=freedreno -Dvulkan-drivers= -Dfreedreno-kmds=msm \
	-Dllvm=disabled -Dgles1=disabled -Dgles2=enabled -Dopengl=true \
	-Dzstd=disabled -Dzlib=disabled -Dexpat=disabled -Dxmlconfig=disabled \
	-Dvalgrind=disabled -Dlibunwind=disabled -Dlmsensors=disabled \
	-Dbuild-tests=false -Dshader-cache=disabled -Dperfetto=false \
	-Dgallium-va=disabled -Dgallium-rusticl=false -Dtools= \
	-Dhtml-docs=disabled -Ddisplay-info=disabled -Dteflon=false "$@"
