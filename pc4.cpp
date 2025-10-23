#include <iostream>
#include <vector>
#include <unordered_map>
#include <tuple>
#include <string>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <limits>
#include <chrono>

using namespace std;

// ---------- STRUCTURE ----------
struct Simplex {
    double time;
    int dim;
    vector<int> vert; // sorted vector of vertices
};

// ---------- READ FILTRATION ----------
vector<Simplex> read_filtration(const string& filename) {
    vector<Simplex> filtration;
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file " << filename << endl;
        return filtration;
    }

    string line;
    while (getline(file, line)) {
        stringstream ss(line);
        Simplex s;
        ss >> s.time >> s.dim;
        int v;
        vector<int> verts;
        while (ss >> v) verts.push_back(v);
        sort(verts.begin(), verts.end());
        s.vert = verts;
        filtration.push_back(s);
    }

    sort(filtration.begin(), filtration.end(),
         [](const Simplex& a, const Simplex& b){ return a.time < b.time; });

    return filtration;
}

// ---------- HASH FUNCTION FOR VECTOR<int> ----------
struct VecHash {
    size_t operator()(const vector<int>& v) const {
        size_t h = 0;
        for (int x : v)
            h ^= hash<int>{}(x) + 0x9e3779b9 + (h << 6) + (h >> 2);
        return h;
    }
};

// ---------- BOUNDARY MATRIX ----------
vector<vector<int>> boundary_matrix(const vector<Simplex>& filtration) {
    unordered_map<vector<int>, int, VecHash> index_map;
    for (size_t i = 0; i < filtration.size(); ++i)
        index_map[filtration[i].vert] = static_cast<int>(i);

    vector<vector<int>> boundary(filtration.size());
    cout << "Computing boundary matrix..." << endl;

    for (size_t j = 0; j < filtration.size(); ++j) {
        const auto& s = filtration[j];
        if (s.dim == 0) continue; // 0-dimensional simplex has empty boundary
        for (size_t k = 0; k < s.vert.size(); ++k) {
            vector<int> face = s.vert;
            face.erase(face.begin() + k); // remove vertex
            auto it = index_map.find(face);
            if (it != index_map.end()) boundary[j].push_back(it->second);
        }
        sort(boundary[j].begin(), boundary[j].end()); // ensure sorted
    }
    return boundary;
}

// ---------- XOR TWO SORTED VECTORS ----------
vector<int> xor_columns(const vector<int>& a, const vector<int>& b) {
    vector<int> res;
    size_t i = 0, j = 0;
    while (i < a.size() || j < b.size()) {
        int va = (i < a.size()) ? a[i] : numeric_limits<int>::max();
        int vb = (j < b.size()) ? b[j] : numeric_limits<int>::max();
        if (va == vb) { ++i; ++j; }          // cancel out (mod 2)
        else if (va < vb) { res.push_back(va); ++i; }
        else { res.push_back(vb); ++j; }
    }
    return res;
}

// ---------- REDUCE BOUNDARY MATRIX ----------
vector<vector<int>> reduce_boundary_matrix(vector<vector<int>> boundary) {
    unordered_map<int,int> pivots;
    cout << "Reducing boundary matrix..." << endl;

    for (size_t j = 0; j < boundary.size(); ++j) {
        while (!boundary[j].empty() && pivots.count(boundary[j].back())) {
            int i = pivots[boundary[j].back()];
            boundary[j] = xor_columns(boundary[j], boundary[i]);
        }
        if (!boundary[j].empty())
            pivots[boundary[j].back()] = static_cast<int>(j);
    }
    return boundary;
}

// ---------- EXTRACT BARCODES ----------
vector<tuple<int,double,double>> extract_barcodes(
    const vector<vector<int>>& reduced,
    const vector<Simplex>& filtration)
{
    vector<tuple<int,int,int>> barcodes_idx;
    vector<bool> paired(filtration.size(), false);

    for (size_t j = 0; j < reduced.size(); ++j) {
        if (!reduced[j].empty()) {
            int low = reduced[j].back();
            barcodes_idx.emplace_back(filtration[low].dim, low, static_cast<int>(j));
            paired[low] = true;
            paired[j] = true;
        }
    }

    for (size_t i = 0; i < filtration.size(); ++i) {
        if (!paired[i]) barcodes_idx.emplace_back(filtration[i].dim, i, -1);
    }

    sort(barcodes_idx.begin(), barcodes_idx.end(),
         [&](const auto& a, const auto& b){
             int da, ba, ea, db, bb, eb;
             tie(da, ba, ea) = a;
             tie(db, bb, eb) = b;
             if (da != db) return da < db;
             if (ba != bb) return ba < bb;
             double dea = (ea==-1)? numeric_limits<double>::infinity() : ea;
             double deb = (eb==-1)? numeric_limits<double>::infinity() : eb;
             return dea < deb;
         });

    vector<tuple<int,double,double>> barcodes;
    for (auto& [dim,birth_idx,death_idx] : barcodes_idx) {
        double birth = filtration[birth_idx].time;
        double death = (death_idx==-1)? numeric_limits<double>::infinity()
                                      : filtration[death_idx].time;
        barcodes.emplace_back(dim,birth,death);
    }

    return barcodes;
}

// ---------- PRINT BARCODES ----------
void print_barcodes(const vector<tuple<int,double,double>>& barcodes) {
    for (auto& [dim,birth,death] : barcodes) {
        cout << "Dimension: " << dim
             << ", Birth: " << birth
             << ", Death: " << ((death==numeric_limits<double>::infinity())?"inf":to_string(death))
             << endl;
    }
}

// ---------- MAIN ----------
int main() {
    using namespace std::chrono;
    auto t_start = high_resolution_clock::now();

    cout << "Reading filtration..." << endl;
    auto filtration = read_filtration("filtrations/filtration_D.txt");
    cout << "Simplices: " << filtration.size() << endl;

    auto t1 = high_resolution_clock::now();
    auto B = boundary_matrix(filtration);
    auto t2 = high_resolution_clock::now();

    auto reduced = reduce_boundary_matrix(B);
    auto t3 = high_resolution_clock::now();

    auto barcodes = extract_barcodes(reduced, filtration);
    auto t4 = high_resolution_clock::now();

    print_barcodes(barcodes);

    cout << "Time read filtration: " << duration_cast<milliseconds>(t1-t_start).count() << " ms\n";
    cout << "Time boundary matrix: " << duration_cast<milliseconds>(t2-t1).count() << " ms\n";
    cout << "Time reduce: " << duration_cast<milliseconds>(t3-t2).count() << " ms\n";
    cout << "Time extract barcodes: " << duration_cast<milliseconds>(t4-t3).count() << " ms\n";

    return 0;
}
