INPUT_FULL = $(shell find input -type f -name "*.flo")
INPUT := $(INPUT_FULL:input/%.flo=%)
OUTPUT_DIR := output
EXE := $(addprefix $(OUTPUT_DIR)/,$(INPUT))
S := $(addsuffix .S,$(EXE))
XML := $(addsuffix .xml,$(EXE))
TXT := $(addsuffix .txt,$(EXE))

build: $(EXE)
asm: $(S)
syntatic: $(XML)
lexical: $(TXT)
all: $(TXT)  $(XML) $(S) $(EXE)
clean:
	@rm -r $(OUTPUT_DIR)

$(OUTPUT_DIR)/%: $(OUTPUT_DIR)/%.S
	@echo "Compilation: $*"
	@arm-linux-gnueabi-gcc $@.S -static -o $@;

$(OUTPUT_DIR)/%.S: input/%.flo
	@echo "Generation de l'ASM: $*"
	@mkdir -p $(OUTPUT_DIR)/$(dir $*)
	@python3 generation_code.py --arm -o $(OUTPUT_DIR)/$*.S $<

$(OUTPUT_DIR)/%.xml: input/%.flo
	@echo "Analyse syntaxique: $*"
	@mkdir -p $(OUTPUT_DIR)/$(dir $*)
	@python3 analyse_syntaxique.py $< > $(OUTPUT_DIR)/$*.xml

$(OUTPUT_DIR)/%.txt: input/%.flo
	@echo "Analyse lexicale: $*"
	@mkdir -p $(OUTPUT_DIR)/$(dir $*)
	@python3 analyse_lexicale.py $< > $(OUTPUT_DIR)/$*.txt
