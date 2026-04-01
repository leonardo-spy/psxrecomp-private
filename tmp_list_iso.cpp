#include <cstdio>
#include "iso_reader.h"

void list_recursive(PS1::ISOReader& iso, const std::string& path, int depth) {
    auto files = iso.ListFiles(path);
    for (auto& f : files) {
        for (int i = 0; i < depth; i++) printf("  ");
        printf("%-30s LBA=%5u Size=%8u %s\n", f.name.c_str(), f.lba, f.size,
               f.is_directory ? "[DIR]" : "");
        if (f.is_directory && f.name != "." && f.name != "..") {
            std::string sub = path.empty() ? f.name : path + "/" + f.name;
            list_recursive(iso, sub, depth + 1);
        }
    }
}

int main() {
    PS1::ISOReader iso;
    if (!iso.Open("C:\\Users\\Leona\\Documents\\GitHub\\psxrecomp\\CastlevaniaRecomp\\isos\\Castlevania - Symphony of the Night (USA).cue")) {
        fprintf(stderr, "Failed to open\n");
        return 1;
    }
    printf("Volume: %s\n", iso.GetVolumeID().c_str());
    printf("Root dir: LBA=%u size=%u\n", iso.GetRootDirectory().lba, iso.GetRootDirectory().size);
    list_recursive(iso, "", 0);
    return 0;
}
