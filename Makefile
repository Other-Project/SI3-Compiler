INPUT := $(basename $(notdir $(wildcard input/*.flo)))
OUTPUT_DIR := output

flo_vers_exercutable: $(addprefix $(OUTPUT_DIR)/,$(INPUT))

$(OUTPUT_DIR)/%: input/%.flo
	@echo "Compilation: $*"
	@if python3 generation_code.py -arm $< > $(OUTPUT_DIR)/$*.S ; \
	then \
		arm-linux-gnueabi-gcc $@.S -static -o $@; \
	else \
		echo "Erreur: La génération du code pour $< a échoué"; \
	fi
