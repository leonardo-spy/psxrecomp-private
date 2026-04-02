cmake_minimum_required(VERSION 3.20)
project(CastlevaniaRecomp C CXX)

set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Path to the PSXRecomp framework (this repository).
set(PSXRECOMP_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." CACHE PATH "Path to psxrecomp root")

# Generated C basename from the recompiler output.
set(GAME_BASENAME "castlevania" CACHE STRING "Generated C basename")

# PS1 executable filename found in the disc image.
set(GAME_EXE_FILENAME "SLUS_000.67" CACHE STRING "PS1 executable filename")

# 0 skips disc CRC verification in launcher.
set(GAME_EXPECTED_CRC32 "0" CACHE STRING "Expected disc CRC32")

# Display thread entry detected from runtime traces for SLUS_000.67.
set(GAME_DISPLAY_ENTRY "0x800191E0" CACHE STRING "Display thread entry address")

# Entry point for Castlevania SOTN (USA) executable.
set(GAME_ENTRY_ADDR "0x80010DF4" CACHE STRING "Compiled entry point address")

set(GENERATED_FULL "${CMAKE_CURRENT_LIST_DIR}/generated/${GAME_BASENAME}_full.c")
set(GENERATED_DISPATCH "${CMAKE_CURRENT_LIST_DIR}/generated/${GAME_BASENAME}_dispatch.c")

if(NOT EXISTS "${GENERATED_FULL}" OR NOT EXISTS "${GENERATED_DISPATCH}")
    message(FATAL_ERROR
        "Missing generated sources. Run:\n"
        "  ${PSXRECOMP_ROOT}/build/recompiler/PSXRecomp.exe isos/${GAME_EXE_FILENAME}\n"
        "Then set GAME_BASENAME if needed (current: ${GAME_BASENAME})."
    )
endif()

include(FetchContent)
include("${PSXRECOMP_ROOT}/runner/runner.cmake")

# GLFW
FetchContent_Declare(glfw
    GIT_REPOSITORY https://github.com/glfw/glfw.git
    GIT_TAG        3.3.8
)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(glfw)

# fmt
FetchContent_Declare(fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        10.1.1
)
FetchContent_MakeAvailable(fmt)

add_library(glad STATIC ${PSXRECOMP_GLAD_SOURCES})
target_include_directories(glad PUBLIC ${PSXRECOMP_GLAD_INCLUDE_DIRS})

add_executable(CastlevaniaRecomp
    extras.cpp
    ${PSXRECOMP_RUNNER_SOURCES}
    ${GENERATED_FULL}
    ${GENERATED_DISPATCH}
)

target_include_directories(CastlevaniaRecomp PRIVATE
    ${PSXRECOMP_RUNNER_INCLUDE_DIRS}
    ${CMAKE_CURRENT_LIST_DIR}/generated
)

target_link_libraries(CastlevaniaRecomp PRIVATE glfw glad fmt)

if(WIN32)
    # opengl32: OpenGL rendering
    # winmm: multimedia timer (timeBeginPeriod)
    # ws2_32: Winsock2 for debug_server TCP
    # comdlg32: file open dialog in launcher
    target_link_libraries(CastlevaniaRecomp PRIVATE opengl32 winmm ws2_32 comdlg32)
endif()

target_compile_definitions(CastlevaniaRecomp PRIVATE
    GAME_WINDOW_TITLE="Castlevania Recomp"
    GAME_EXE_FILENAME="${GAME_EXE_FILENAME}"
    GAME_EXPECTED_CRC32=${GAME_EXPECTED_CRC32}
    GAME_DISPLAY_ENTRY=${GAME_DISPLAY_ENTRY}
    GAME_ENTRY_ADDR=${GAME_ENTRY_ADDR}
)

# Stack overflow prevention: mips_interpret has ~8-16KB stack frames.
# -fstack-clash-protection forces GCC to probe every page when allocating large
# frames, preventing the "guard page jump" that causes ACCESS_VIOLATION on Windows.
if(MINGW)
    target_compile_options(CastlevaniaRecomp PRIVATE -fstack-clash-protection)
endif()

# Reserve 16MB stack to handle large interpreter frames
if(MINGW)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--stack,16777216")
endif()

add_custom_command(TARGET CastlevaniaRecomp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${PSXRECOMP_ROOT}/runner/assets/keyconfig.ini"
        "$<TARGET_FILE_DIR:CastlevaniaRecomp>/keyconfig.ini"
    COMMENT "Copying keyconfig.ini to output directory"
)
