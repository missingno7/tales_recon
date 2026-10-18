# ducktales: the SDL3 port (docs/sdl3-port.md). The game is the Amiga build's staged
# translation units (tools/game_build.py) translated by tools/port_gen.py into
# build/port-gen (never committed), compiled together with the emulated Amiga below.
# A 32-bit build: the game's records hold 4-byte pointers, as on the 68000.
cmake_minimum_required(VERSION 3.20)

if(NOT DEFINED CMAKE_C_COMPILER)
  set(CMAKE_C_COMPILER "C:/msys64/mingw32/bin/gcc.exe" CACHE FILEPATH "MinGW-w64 i686 gcc")
endif()

project(ducktales_port C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_EXTENSIONS ON)

set(REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/..")
set(PORT_GEN_DIR "${REPO_ROOT}/build/port-gen")
set(SDL3_ROOT "C:/tools/sdl3-3.4.16-mingw/SDL3-3.4.16/i686-w64-mingw32" CACHE PATH "SDL3 installation (i686)")
set(SDL3_DIR "${SDL3_ROOT}/lib/cmake/SDL3" CACHE PATH "SDL3 package")

find_package(Python3 COMPONENTS Interpreter REQUIRED)
find_package(SDL3 CONFIG REQUIRED)

# ---- the game: translated at configure time from the staged Amiga build ----
execute_process(
  COMMAND "${Python3_EXECUTABLE}" -B "${REPO_ROOT}/tools/port_gen.py"
          --source "${REPO_ROOT}/build/game" --output "${PORT_GEN_DIR}"
          --override-dir "${CMAKE_CURRENT_SOURCE_DIR}/override"
  RESULT_VARIABLE PORT_GEN_RESULT)
if(NOT PORT_GEN_RESULT EQUAL 0)
  message(FATAL_ERROR "tools/port_gen.py failed (run tools/game_build.py --build first)")
endif()
file(GLOB GAME_SOURCES "${PORT_GEN_DIR}/*.c")
set(GAME_ASM "${PORT_GEN_DIR}/materialization.s" "${PORT_GEN_DIR}/asm_symbols.s")
# Aztec C semantics: 16-bit int made explicit by the generator, wrapping arithmetic;
# -O0 because the game busy-waits on globals its interrupt servers change.
set_source_files_properties(${GAME_SOURCES} PROPERTIES
  COMPILE_OPTIONS "-O0;-w;-fpermissive;-fwrapv;-fno-strict-aliasing")
set_source_files_properties(${GAME_ASM} PROPERTIES LANGUAGE C COMPILE_OPTIONS "-x;assembler")

# ---- the emulated Amiga ----
set(PLATFORM_SOURCES
  "${CMAKE_CURRENT_SOURCE_DIR}/main.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/adf.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/os_exec.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/os_dos.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/os_graphics.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/os_misc.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/runtime.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/asm_ports.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/m68k.c"
  "${CMAKE_CURRENT_SOURCE_DIR}/paula.c")
set_source_files_properties(${PLATFORM_SOURCES} PROPERTIES
  COMPILE_OPTIONS "-O2;-Wall;-fwrapv;-fno-strict-aliasing")

add_executable(ducktales ${GAME_SOURCES} ${GAME_ASM} ${PLATFORM_SOURCES})
target_include_directories(ducktales PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_SOURCE_DIR}/include")
target_link_libraries(ducktales PRIVATE SDL3::SDL3)
if(MINGW)
  target_link_options(ducktales PRIVATE -static-libgcc)
endif()
set_target_properties(ducktales PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
add_custom_command(TARGET ducktales POST_BUILD
  COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${SDL3_ROOT}/bin/SDL3.dll" "$<TARGET_FILE_DIR:ducktales>/SDL3.dll"
  VERBATIM)
