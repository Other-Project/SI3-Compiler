INPUT := $(basename $(notdir $(wildcard input/*.flo)))
OUTPUT_DIR := output

build: $(addprefix $(OUTPUT_DIR)/,$(INPUT))
syntatic: $(addsuffix .xml,$(addprefix $(OUTPUT_DIR)/,$(INPUT)))
clean:
	rm $(OUTPUT_DIR)/*

$(OUTPUT_DIR)/%: input/%.flo
	@echo "Compilation: $*"
	@if python3 generation_code.py -arm $< > $(OUTPUT_DIR)/$*.s ; \
	then \
		arm-linux-gnueabi-gcc $@.s -static -o $@; \
	else \
		echo "Erreur: La génération du code pour $< a échoué"; \
	fi


$(OUTPUT_DIR)/%.xml: input/%.flo
	@echo "Analyse syntaxique: $*"
	@python3 analyse_syntaxique.py $< > $(OUTPUT_DIR)/$*.xml
