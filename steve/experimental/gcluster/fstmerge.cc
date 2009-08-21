#include <iostream>
#include <fstream>
#include <algorithm>
#include <ctime>

#include <google/protobuf/repeated_field.h>

#include "proto/worddata.pb.h"

using namespace std;
using namespace google::protobuf;
using namespace worddata;

// Parse a line from a CSV file.
void ParseCSVLine(const string& line, char delimeter, vector<string>* record) {
  int linepos = 0;
  int inquotes = false;
  string cur_field;

  record->clear();

  while (linepos < line.length() && line[linepos] != 0) {
    char c = line[linepos];
    if (!inquotes && cur_field.length() == 0 && c == '"') {
      // Beginning of a quoted string.
      inquotes = true;
    } else if (inquotes && c == '"') {
      if (linepos + 1 < line.length() && line[linepos + 1] == '"') {
        // Two double quotes in a row, which signifies a single actual quote.
        cur_field.push_back(c);
        linepos++;
      } else {
        // A closing quotation mark means the end of the quoted string.
        inquotes = false;
      }
    } else if (!inquotes && c == delimeter) {
      // End of the current field.
      record->push_back(cur_field);
      cur_field = "";
    } else if (!inquotes && (c == '\r' || c == '\n')) {
      // Encountered an end of line that's outside of a quotes - we're done.
      break;
    } else {
      // This is a normal character, treat it as such.
      cur_field.push_back(c);
    }
    linepos++;
  }
  record->push_back(cur_field);
  return;
}

typedef map<string, WordData> Lexicon;

Lexicon::iterator FindOrInsertIntoLexicon(const string& terminal, Lexicon* lexicon) {
  Lexicon::iterator ret = lexicon->find(terminal);
  if (ret == lexicon->end()) {
    WordData new_worddata;
    new_worddata.set_terminal(terminal);
    ret = lexicon->insert(make_pair(terminal, new_worddata)).first;
  }
  return ret;
}

Lexicon::iterator FindOrInsertIntoLexiconWithCached(const string& terminal,
                                                    Lexicon::iterator cached_it,
                                                    Lexicon* lexicon) {
  if (cached_it != lexicon->end() && cached_it->first == terminal) {
    return cached_it;
  } else {
    return FindOrInsertIntoLexicon(terminal, lexicon);
  }
}

Lexicon::iterator HandleCanonicalPositionLine(const vector<string>& record,
                                              Lexicon::iterator previous_records_it,
                                              Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexiconWithCached(record[0], previous_records_it, lexicon);
  int count = atoi(record[2].c_str());
  CanonicalPositionDistribution* position_distribution = it->second.mutable_position_distribution();

  if (record[1] == "beg") {
    position_distribution->set_beg(count);
  } else if (record[1] == "mid") {
    position_distribution->set_mid(count);
  } else if (record[1] == "end") {
    position_distribution->set_end(count);
  } else if (record[1] == "solo") {
    position_distribution->set_solo(count);
  }

  return it;
}

void AddTerminalToDistribution(const string& terminal, int count, SampledTerminalDistribution* distribution) {
  distribution->set_observed_count(distribution->observed_count() + 1);
  distribution->set_observed_weight(distribution->observed_weight() + count);
  TerminalCount* terminal_count = distribution->add_terminals();
  terminal_count->set_terminal(terminal);
  terminal_count->set_weight(count);
}

Lexicon::iterator HandleTopTerminalsBeforeLine(const vector<string>& record,
                                               Lexicon::iterator previous_records_it,
                                               Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexiconWithCached(record[0], previous_records_it, lexicon);
  int count = atoi(record[2].c_str());
  AddTerminalToDistribution(record[1], count, it->second.mutable_terminals_before());
  return it;
}

Lexicon::iterator HandleTopTerminalsAfterLine(const vector<string>& record,
                                              Lexicon::iterator previous_records_it,
                                              Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexiconWithCached(record[0], previous_records_it, lexicon);
  int count = atoi(record[2].c_str());
  AddTerminalToDistribution(record[1], count, it->second.mutable_terminals_after());
  return it;
}

Lexicon::iterator HandleTotalCountsBeforeLine(const vector<string>& record,
                                              Lexicon::iterator previous_records_it,
                                              Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexicon(record[0], lexicon);
  int count = atoi(record[1].c_str());
  it->second.mutable_terminals_before()->set_total_weight(count);
  return it;
}

Lexicon::iterator HandleTotalCountsAfterLine(const vector<string>& record,
                                             Lexicon::iterator previous_records_it,
                                             Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexicon(record[0], lexicon);
  int count = atoi(record[1].c_str());
  it->second.mutable_terminals_after()->set_total_weight(count);
  return it;
}

Lexicon::iterator HandleUniqueTerminalsBeforeLine(const vector<string>& record,
                                                 Lexicon::iterator previous_records_it,
                                                 Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexicon(record[0], lexicon);
  int count = atoi(record[1].c_str());
  it->second.mutable_terminals_before()->set_total_count(count);
  return it;
}

Lexicon::iterator HandleUniqueTerminalsAfterLine(const vector<string>& record,
                                                 Lexicon::iterator previous_records_it,
                                                 Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexicon(record[0], lexicon);
  int count = atoi(record[1].c_str());
  it->second.mutable_terminals_after()->set_total_count(count);
  return it;
}

Lexicon::iterator HandleShardedTopTerminalsLine(const vector<string>& record,
                                                Lexicon::iterator previous_records_it,
                                                Lexicon* lexicon) {
  Lexicon::iterator it = FindOrInsertIntoLexicon(record[1], lexicon);
  int count = atoi(record[2].c_str());
  it->second.set_weight(count);
  return it;
}


typedef Lexicon::iterator (*HandleLineCallback)(const vector<string>&, Lexicon::iterator, Lexicon*);

bool ProcessFile(const string& path, HandleLineCallback handle_line_callback, Lexicon* lexicon) {
  ifstream file(path.c_str(), ios::in | ios::ate);

  if (file.fail()) {
    cout << "could not find [" << path << "]" << endl;
    return false;
  }

  float file_size = file.tellg();
  file.seekg(0, ios::beg);

  vector<string> record;
  string line;
  Lexicon::iterator current_records_it(lexicon->end());
  int line_number = 0;

  clock_t start_time = clock();

  while (getline(file, line) && file.good()) {
    line_number += 1;
    ParseCSVLine(line, ',', &record);
    current_records_it = handle_line_callback(record, current_records_it, lexicon);
    if (line_number % 10000 == 0) {
      float percent_complete = 100 * file.tellg() / file_size;
      cout << path << ": processed " << line_number << " lines - " << percent_complete << endl;
    }
  }

  clock_t end_time = clock();
  float time_taken = static_cast<float>(end_time - start_time) / CLOCKS_PER_SEC;
  cout << "done processing [" << path << "], read " << line_number << " lines in " << time_taken << " seconds" << endl;

  file.close();
  return true;
}

bool WordDataCmp(const WordData& a, const WordData& b) {
  return a.terminal() > b.terminal();
}

bool TerminalCountCmp(const TerminalCount& a, const TerminalCount& b) {
  return a.terminal() > b.terminal();
}

void SortTerminalDistribution(SampledTerminalDistribution* distribution) {
  RepeatedPtrField<TerminalCount>* terminals = distribution->mutable_terminals();
  sort(terminals->begin(), terminals->end(), TerminalCountCmp);
}

bool Foobar() {
  string output_path = "/usr/local/google/home/fedele/aobitu/data/worddata.2.plf";

  ofstream file(output_path.c_str(), ios::out | ios::binary);
  if (file.fail()) {
    cout << "could not open output file [" << output_path << "]" << endl;
    return false;
  }

  clock_t start_time = clock();

  Lexicon lexicon;
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/canonical_positions.csv",
              HandleCanonicalPositionLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/top_terminals_before.csv",
              HandleTopTerminalsBeforeLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/top_terminals_after.csv",
              HandleTopTerminalsAfterLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/total_counts_before.csv",
              HandleTotalCountsBeforeLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/total_counts_after.csv",
              HandleTotalCountsAfterLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/unique_terminals_before.csv",
              HandleUniqueTerminalsBeforeLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/worddata1/20090806/unique_terminals_after.csv",
              HandleUniqueTerminalsAfterLine, &lexicon);
  ProcessFile("/usr/local/google/home/fedele/aobitu/output/lexicon1/20090806/top_terminals.csv",
              HandleShardedTopTerminalsLine, &lexicon);

  cout << "done reading in input, writing output now..." << endl;

  int n = 0;
  for (Lexicon::iterator it = lexicon.begin(); it != lexicon.end(); ++it, ++n) {
    SortTerminalDistribution(it->second.mutable_terminals_before());
    SortTerminalDistribution(it->second.mutable_terminals_after());
    string serialized_worddata;
    it->second.SerializeToString(&serialized_worddata);
    int record_size = serialized_worddata.length();
    file.write((char*) &record_size, 4);
    file.write(serialized_worddata.c_str(), record_size);
    if (n % 1000 == 0) {
      cout << "wrote " << n << " / " << lexicon.size() << " records" << endl;
    }
  }
  file.close();

  float time_taken = static_cast<float>(clock() - start_time) / CLOCKS_PER_SEC;
  cout << "done!  total time taken: " << time_taken << " seconds" << endl;
  return true;
}

int main(int argc, char* argv[]) {
  Foobar();
  return 0;

  // Keeping the following code around as it contains an example of reading
  // WordData from a protolist file.
  /*
  ifstream file("/tmp/gcluster-preprocess-0-of-10.plf", ios::in | ios::binary | ios::ate);
  if (!file.is_open()) {
    cout << "could not open file" << endl;
    return 0;
  }
  int file_size = file.tellg();
  cout << "file size: " << file_size << endl;
  file.seekg(0, ios::beg);

  vector<WordData> all_worddata;
  int num_records_processed = 0;

  while (file.tellg() < file_size) {
    int record_size;
    file.read((char*) &record_size, 4);
    char* buffer = new char[record_size];
    file.read(buffer, record_size);
    WordData worddata;
    worddata.ParseFromString(buffer);
    all_worddata.push_back(worddata);
    num_records_processed += 1;
    if (num_records_processed % 1000 == 0) {
      cout << "processed " << num_records_processed << " records" << endl;
    }
  }

  cout << "done reading, processed " << num_records_processed << endl;

  sort(all_worddata.begin(), all_worddata.end(), WordDataCmp);

  string cur_key = "";
  WordData cur_proto;
  for (int i = 0; i < all_worddata.size(); ++i) {
    const WordData& worddata = all_worddata[i];
    if (worddata.terminal() != cur_key) {
      if (!cur_key.empty()) {
        // Output the current (now finished) proto.
        // cout << cur_proto.DebugString() << endl;
      }
      // Make a new proto.
      cur_proto = WordData();
      cur_key = worddata.terminal();
    }
    cur_proto.MergeFrom(worddata);
  }
  */
}
