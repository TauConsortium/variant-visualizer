# Script to plot the domains of a gene.
# Juliana Acosta-Uribe
# Copyright UCSB. August 2022


# Example made with NPC1
# Requires dataframe with start - end coordinates and type of domain

library(ggplot2)
library(ggrepel)

setwd("~/Documents/Kosik Lab -UCSB/NPC1")
NPC1_domains = read.delim("NPC1_domains.txt")
NPC1_variants = read.delim("NPC1_variants.txt")


# 1. Plot the gene, no variants

gene_plot = ggplot(data=NPC1_domains, 
                  aes(y = 0, x = AA_start, colour = Domain)) +
              geom_segment(aes(yend = 0, xend = AA_end), size = 8) +
              scale_color_manual(values = c("yellowgreen", "cyan3 ", "blue")) +
              theme_minimal() +
              theme(panel.border = element_blank(),
                    panel.grid.major = element_blank(),
                    panel.grid.minor = element_blank(),
                    axis.title.y = element_blank(),
                    axis.ticks.length.y = unit(0, "mm"),
                    axis.text.y = element_blank(), 
                    legend.position = "bottom") +
              scale_x_continuous(breaks = seq(0,2000,200)) +
              coord_fixed(200) +
              labs(x = "NPC1")

plot(gene_plot)


# 2. Plot Gene + variants
  
var_plot = ggplot(data = NPC1_variants,
                  aes(x = AA, y = 0, 
                      label = variant)) + 
              labs(x = "NPC1") + 
  
              # plot gene domains in the background 
              geom_segment(data = NPC1_domains,
                           aes(x = AA_start, 
                               xend = AA_end, 
                               y = 0, 
                               yend = 0, 
                               colour = Domain),
                           size = 5,
                           inherit.aes = FALSE) +
              scale_color_manual(values = c("yellowgreen", "cyan3 ", "blue")) +
  
              # add a point for each variant
              geom_point(color = ifelse(NPC1_variants$control == 0, "violetred", "black")) +
  
              # give the name of each variant
              geom_text_repel(force_pull   = 0, # do not pull toward data points
                              nudge_y = 0.1,
                              direction = "x",
                              angle = 90,
                              hjust = 0,
                              segment.size = 0.1,
                              colour = ifelse(NPC1_variants$control == 0, "violetred", "black")) +
              # set up limits
              xlim(0, 1250) +
              ylim(0, 0.5) +
  
              # set up your theme
              theme_minimal() +  
              theme(panel.border = element_blank(),
                    panel.grid.major = element_blank(),
                    panel.grid.minor = element_blank(),
                    axis.title.y = element_blank(),
                    axis.ticks.length.y = unit(0, "mm"),
                    axis.text.y = element_blank(), 
                    #axis.text.y = element_text(face = "bold", size = 12),
                    legend.position = "bottom") 
plot(var_plot)


# 3. Plot Gene variants and carrier counts

var_plot_counts = var_plot +
  geom_label_repel(data = NPC1_variants,
                   aes(label=case),
                   nudge_y = 0.2, #Starting position of y label
                   min.segment.length = Inf, # Never draw any line segments 
                   direction = "x", # Move in x axis
                   hjust = 0.5, # Center align
                   colour = ifelse(NPC1_variants$control == 0, "violetred", "black")) +
  annotate("text", x = 0, y = 0.2, label = "Cases") +
  geom_label_repel(data = NPC1_variants,
                   aes(label=control),
                   nudge_y = 0.25, #Starting position of y label
                   min.segment.length = Inf, # Never draw any line segments 
                   direction = "x", # Move in x axis
                   hjust = 0.5, # Center align
                   colour = ifelse(NPC1_variants$control == 0, "violetred", "black")) +
  annotate("text", x = 0, y = 0.25, label = "Controls")

plot(var_plot_counts)  
