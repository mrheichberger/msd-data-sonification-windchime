# pico_sdk_import.cmake
# Minimal helper that expects PICO_SDK_PATH env var to be set.

if (DEFINED ENV{PICO_SDK_PATH} AND (NOT PICO_SDK_PATH))
    set(PICO_SDK_PATH $ENV{PICO_SDK_PATH})
endif()

if (NOT PICO_SDK_PATH)
    message(FATAL_ERROR "PICO_SDK_PATH not specified. "
                        "Set it as an environment variable.")
endif()

include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
