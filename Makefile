INPUT := $(basename $(notdir $(wildcard input/*.flo)))
OUTPUT_DIR := output
EXE := $(addprefix $(OUTPUT_DIR)/,$(INPUT))
S := $(addsuffix .S,$(EXE))
XML := $(addsuffix .xml,$(EXE))
TXT := $(addsuffix .txt,$(EXE))

all: $(TXT)  $(XML) $(S) $(EXE)
build: $(EXE)
asm: $(S)
syntatic: $(XML)
lexical: $(TXT)
clean:
	@rm $(OUTPUT_DIR)/*

$(OUTPUT_DIR)/%: $(OUTPUT_DIR)/%.S
	@echo "Compilation: $*"
	@-arm-linux-gnueabi-gcc $@.s -static -o $@;

$(OUTPUT_DIR)/%.S: input/%.flo
	@echo "Generation de l'ASM: $*"
	@-python3 generation_code.py -arm $< > $(OUTPUT_DIR)/$*.S

$(OUTPUT_DIR)/%.xml: input/%.flo
	@echo "Analyse syntaxique: $*"
	@-python3 analyse_syntaxique.py $< > $(OUTPUT_DIR)/$*.xml

	
$(OUTPUT_DIR)/%.txt: input/%.flo
	@echo "Analyse lexicale: $*"
	@-python3 analyse_lexicale.py $< > $(OUTPUT_DIR)/$*.txt
