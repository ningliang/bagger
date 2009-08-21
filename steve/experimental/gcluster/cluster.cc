#include <iostream>
#include <fstream>
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <cmath>

#include <google/protobuf/repeated_field.h>

#include "proto/worddata.pb.h"

using namespace std;
using namespace google::protobuf;
using namespace worddata;


class ReadBuffer {
 public:
  ReadBuffer() : buffer_(NULL), buffer_size_(0) { }
  ~ReadBuffer() { delete buffer_; }

  void ReadString(ifstream& f, int size, string* write_to) {
    f.read(GetBuffer(size), size);
    write_to->assign(buffer_, size);
  }

  char* GetBuffer(int size) {
    if (size > buffer_size_) {
      delete buffer_;
      if (buffer_size_ == 0) {
        buffer_size_ = 1024;
      }
      while (buffer_size_ < size) {
        buffer_size_ *= 2;
      }
      buffer_ = new char[buffer_size_];
    }
    return buffer_;
  }

 private:
  char* buffer_;
  int buffer_size_;
};


bool ReadWordData(const string& path, vector<WordData>* worddatas, int number_to_read=-1) {
  ifstream file(path.c_str(), ios::in | ios::binary | ios::ate);
  if (!file.is_open()) {
    cout << "could not open [" << path << "]" << endl;
    return false;
  }
  int file_size = file.tellg();
  file.seekg(0, ios::beg);

  vector<WordData> all_worddata;
  int num_records_processed = 0;

  cout << "file_size = " << file_size << endl;

  ReadBuffer read_buffer;
  string serialized_worddata;

  while (file.tellg() < file_size) {
    int record_size;
    file.read((char*) &record_size, 4);
    read_buffer.ReadString(file, record_size, &serialized_worddata);
    WordData worddata;
    worddata.ParseFromString(serialized_worddata);
    worddatas->push_back(worddata);
    num_records_processed += 1;
    if (number_to_read != -1 && num_records_processed >= number_to_read) {
      break;
    }
    if (num_records_processed % 250 == 0) {
      float percent_complete = 100.0 * file.tellg() / file_size;
      cout << "processed " << num_records_processed << " records (" << percent_complete << "% complete)" << endl;
    }
  }
  cout << "done reading, processed " << num_records_processed << endl;
}



float SampledDistributionDistance(const SampledTerminalDistribution& dist1,
                                  const SampledTerminalDistribution& dist2) {
  // TODO(fedele): is this empty default valid?
  if (dist1.terminals_size() == 0 || dist2.terminals_size() == 0) return 0.0;

  const RepeatedPtrField<TerminalCount>& terminals1 = dist1.terminals();
  const RepeatedPtrField<TerminalCount>& terminals2 = dist2.terminals();

  RepeatedPtrField<TerminalCount>::const_iterator i1(terminals1.begin()), i2(terminals2.begin());

  int overlap_count = 0;
  double distance_12 = 0.0, distance_21 = 0.0;

  double p1, p2;
  double p1_unobserved = dist1.total_count() - dist1.observed_count();
  double p1_guess_weight = (dist1.total_weight() - dist1.observed_weight()) / (dist1.total_count() - dist1.observed_count());
  if (isnan(p1_guess_weight)) {
    p1_guess_weight = 0.5;
  }
  double p1_guess = p1_guess_weight / dist1.total_weight();
  double p2_guess_weight = (dist2.total_weight() - dist2.observed_weight()) / (dist2.total_count() - dist2.observed_count());
  if (isnan(p2_guess_weight)) {
    p2_guess_weight = 0.5;
  }
  double p2_guess = p2_guess_weight / dist2.total_weight();

  double missing_1 = 0.0, missing_2 = 0.0;

  bool output = false;

  while (i1 != terminals1.end() && i2 != terminals2.end()) {
    if (i1->terminal() == i2->terminal()) {
      // Overlap!
      if (output) {
        cout << setw(20) << i1->terminal() << setw(8) << i1->weight() << setw(8) << i2->weight();
      }
      overlap_count += 1;
      p1 = i1->weight() / dist1.total_weight();
      p2 = i2->weight() / dist2.total_weight();
      ++i1;
      ++i2;
    } else if (i1->terminal() > i2->terminal()) {
      if (output) {
        cout << setw(20) << i1->terminal() << setw(8) << i1->weight() << setw(8) << "MISSING";
      }
      p1 = i1->weight() / dist1.total_weight();
      missing_1 += p1;
      p2 = p2_guess;
      ++i1;
    } else {
      if (output) {
        cout << setw(20) << i2->terminal() << setw(8) << "MISSING" << setw(8) << i2->weight();
      }
      p1 = p1_guess;
      p2 = i2->weight() / dist2.total_weight();
      missing_2 += p2;
      ++i2;
    }

    double err1 = p1 * (log(p1) - log(p2));
    double err2 = p2 * (log(p2) - log(p1));
    distance_12 += err1;
    distance_21 += err2;

    if (output) {
      cout << " p1 = " << p1 << " p2 = " << p2 << " err1 = " << err1 << " err2 " << err2 << endl;
    }
  }

  double ret = (distance_12 + distance_21) / 2;
  if (output) {
    cout << " " << setiosflags(ios::fixed) << setprecision(3) << distance_12 << " " << distance_21 << " total: " << ret << endl;
  }

  return ret;
}

void Debug(const WordData& w1, const WordData& w2) {
  cout << "Terminals [" << setw(20) << w1.terminal() << "] vs [" << setw(20) << w2.terminal() << "] ";
  float distance = SampledDistributionDistance(w1.terminals_before(), w2.terminals_before());
}

void PrintClosestAndFurthestTerminals(const WordData& w1, const vector<WordData>& lexicon) {
  vector<pair<double, string> > tmp;
  tmp.reserve(lexicon.size());
  for (vector<WordData>::const_iterator it = lexicon.begin(); it != lexicon.end(); ++it) {
    tmp.push_back(make_pair(SampledDistributionDistance(w1.terminals_before(), it->terminals_before()),
                            it->terminal()));
  }

  sort(tmp.begin(), tmp.end());

  for (int i = 0; i < 10; ++i) {
    cout << tmp[i].first << " " << setiosflags(ios::fixed) << setprecision(2) << tmp[i].second << ",";
  }

  for (int i = max(tmp.size() - 10, (unsigned long) 10); i < tmp.size(); ++i) {
    cout << tmp[i].first << " " << setiosflags(ios::fixed) << setprecision(2) << tmp[i].second << ",";
  }

  cout << endl;
}


int main(int argc, char* argv[]) {
  vector<WordData> lexicon;
  lexicon.reserve(20000);
  ReadWordData("/usr/local/google/home/fedele/aobitu/data/worddata.2.plf", &lexicon);

  cout << "building map..." << endl;
  map<string, int> worddata_indices;
  for (int i = 0; i < lexicon.size(); ++i) {
    worddata_indices.insert(make_pair(lexicon[i].terminal(), i));
  }

  while (true) {
    string input_line;
    cout << "> ";
    getline(cin, input_line);
    if (cin.fail()) {
      break;
    }
    cout << "[" << input_line << "]" << endl;
    map<string, int>::iterator it = worddata_indices.find(input_line);
    if (it != worddata_indices.end()) {
      cout << "computing closest and furthest from " << it->first << "..." << endl;
      PrintClosestAndFurthestTerminals(lexicon[it->second], lexicon);
    } else {
      cout << "not found" << endl;
    }
  }
  cout << endl;
  return 0;

  /*
  for (int i = 0; i < 50; ++i) {
    cout << setiosflags(ios::left) << setw(20) << tmp[i].first << setiosflags(ios::fixed) << setprecision(2) << tmp[i].second << endl;
  }

  for (int i = max(tmp.size() - 50, (unsigned long) 50); i < tmp.size(); ++i) {
    cout << setiosflags(ios::left) << setw(20) << tmp[i].first << setiosflags(ios::fixed) << setprecision(2) << tmp[i].second << endl;
  }
  */
}
