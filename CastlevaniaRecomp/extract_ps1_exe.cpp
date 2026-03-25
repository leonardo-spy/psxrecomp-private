#include <algorithm>
#include <cctype>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "iso_reader.h"

static std::string trim(const std::string& s) {
    size_t b = 0;
    while (b < s.size() && std::isspace(static_cast<unsigned char>(s[b]))) {
        b++;
    }
    size_t e = s.size();
    while (e > b && std::isspace(static_cast<unsigned char>(s[e - 1]))) {
        e--;
    }
    return s.substr(b, e - b);
}

static std::string parse_boot_exe_from_system_cnf(const std::string& cnf_text) {
    std::string text = cnf_text;
    std::replace(text.begin(), text.end(), '\r', '\n');

    size_t pos = 0;
    while (pos < text.size()) {
        size_t nl = text.find('\n', pos);
        if (nl == std::string::npos) {
            nl = text.size();
        }

        std::string line = trim(text.substr(pos, nl - pos));
        std::string upper = line;
        std::transform(upper.begin(), upper.end(), upper.begin(), [](unsigned char c) {
            return static_cast<char>(std::toupper(c));
        });

        if (upper.rfind("BOOT", 0) == 0) {
            size_t cdrom = upper.find("CDROM:");
            if (cdrom != std::string::npos) {
                size_t semicolon = upper.find(';', cdrom);
                std::string path = (semicolon == std::string::npos)
                    ? line.substr(cdrom + 6)
                    : line.substr(cdrom + 6, semicolon - (cdrom + 6));

                path = trim(path);
                path.erase(std::remove(path.begin(), path.end(), '\\'), path.end());
                path = trim(path);

                return path;
            }
        }

        pos = (nl < text.size()) ? nl + 1 : nl;
    }

    return "";
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: extract_ps1_exe <disc.cue> <output_dir>\n";
        return 1;
    }

    const std::string cue_path = argv[1];
    const std::string output_dir = argv[2];

    PS1::ISOReader iso;
    if (!iso.Open(cue_path)) {
        std::cerr << "Failed to open cue/bin: " << cue_path << "\n";
        return 1;
    }

    const size_t cnf_size = iso.GetFileSize("SYSTEM.CNF");
    if (cnf_size == 0) {
        std::cerr << "SYSTEM.CNF not found in disc root\n";
        return 1;
    }

    std::vector<uint8_t> cnf(cnf_size);
    const size_t cnf_read = iso.ReadFile("SYSTEM.CNF", cnf.data(), cnf.size());
    if (cnf_read == 0) {
        std::cerr << "Failed to read SYSTEM.CNF\n";
        return 1;
    }

    const std::string cnf_text(reinterpret_cast<const char*>(cnf.data()), cnf_read);
    const std::string exe_name = parse_boot_exe_from_system_cnf(cnf_text);
    if (exe_name.empty()) {
        std::cerr << "Could not parse BOOT line from SYSTEM.CNF\n";
        return 1;
    }

    const size_t exe_size = iso.GetFileSize(exe_name);
    if (exe_size == 0) {
        std::cerr << "Executable not found in root: " << exe_name << "\n";
        return 1;
    }

    std::vector<uint8_t> exe(exe_size);
    const size_t exe_read = iso.ReadFile(exe_name, exe.data(), exe.size());
    if (exe_read != exe_size) {
        std::cerr << "Failed reading executable bytes: " << exe_name << "\n";
        return 1;
    }

    const std::string out_path = output_dir + "/" + exe_name;
    std::ofstream out(out_path, std::ios::binary);
    if (!out.is_open()) {
        std::cerr << "Failed to open output file: " << out_path << "\n";
        return 1;
    }
    out.write(reinterpret_cast<const char*>(exe.data()), static_cast<std::streamsize>(exe.size()));
    out.close();

    std::cout << "VOLUME: " << iso.GetVolumeID() << "\n";
    std::cout << "EXE: " << exe_name << "\n";
    std::cout << "SIZE: " << exe_size << " bytes\n";
    std::cout << "OUT: " << out_path << "\n";

    return 0;
}
