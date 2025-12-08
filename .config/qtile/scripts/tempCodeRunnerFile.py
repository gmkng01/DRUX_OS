 buttons
        palette_layout = QtWidgets.QHBoxLayout()
        palette_layout.addWidget(QtWidgets.QLabel("Palette:"))
        self.swatch1 = ColorSwatch("#2C3333")
        self.swatch2 = ColorSwatch("#444444")
        palette_layout.addWidget(self.swatch1)
        palette_layout.addWidget(self.swatch2)
        palette_layout.addStretch()
        left.addLayout(palette_layout)