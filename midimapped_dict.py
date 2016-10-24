availableFunctions = {
    'submenu': {
        0: {
            'name': 'Note remap',
            'fn': 'notelist',
            'submenu': {
                0: {'name': 'Learn'},
                1: {'name': 'Delete'}
            }
        },
        1: {
            'name': 'Master volume',
            'functionToMap': 'setvolume',
            'submenu': {
                0: {'name': 'Learn', 'fn': 'Learn'},
                1: {'name': 'Min', 'params': [-70]},
                2: {'name': 'Max', 'params': [0]},
                3: {'name': 'Delete'}
            }
        },
        2: {
            'name': 'Reverb',
            'submenu': {
                0: {
                    'name': 'Room size',
                    'fn': 'roomsize',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Min', 'params': [0]},
                        2: {'name': 'Max', 'params': [100]},
                        3: {'name': 'Delete'}
                    }
                },
                1: {
                    'name': 'Damping',
                    'fn': 'damping',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Min', 'params': [0]},
                        2: {'name': 'Max', 'params': [100]},
                        3: {'name': 'Delete'}
                    }
                },
                2: {
                    'name': 'Wet',
                    'fn': 'wet',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Min', 'params': [0]},
                        2: {'name': 'Max', 'params': [100]},
                        3: {'name': 'Delete'}
                    }
                },
                3: {
                    'name': 'Dry',
                    'fn': 'dry',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Min', 'params': [0]},
                        2: {'name': 'Max', 'params': [100]},
                        3: {'name': 'Delete'}
                    }
                },
                4: {
                    'name': 'Width',
                    'fn': 'width',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Min', 'params': [0]},
                        2: {'name': 'Max', 'params': [100]},
                        3: {'name': 'Delete'}
                    }
                }
            }
        },
        3: {
            'name': 'Voices',
            'fn': 'voices',
            'submenu': {
                0: {
                    'name': 'Voice 1',
                    'fn': 'voice',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Delete'}
                    }
                },
                1: {
                    'name': 'Voice 2',
                    'fn': 'voice',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Delete'}
                    }
                },
                2: {
                    'name': 'Voice 3',
                    'fn': 'voice',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Delete'}
                    }
                },
                3: {
                    'name': 'Voice 4',
                    'fn': 'voice',
                    'submenu': {
                        0: {'name': 'Learn'},
                        1: {'name': 'Delete'}
                    }
                },
            }
        },
        4: {
            'name': 'SamplerBox Navigation',
            'fn': 'sbNav',
            'submenu': {
                0: {
                    'name': 'Left',
                    'fn': 'left',
                    'submenu': {
                        0: {'Learn': None},
                        1: {'Delete': None}
                    }
                },
                1: {
                    'name': 'Right',
                    'fn': 'right',
                    'submenu': {
                        0: {'Learn': None},
                        1: {'Delete': None}
                    }
                },
                2: {
                    'name': 'Enter',
                    'fn': 'enter',
                    'submenu': {
                        0: {'Learn': None},
                        1: {'Delete': None}
                    }
                },
                3: {
                    'name': 'Cancel',
                    'fn': 'cancel',
                    'submenu': {
                        0: {'Learn': None},
                        1: {'Delete': None}
                    }
                }
            }
        }
    }
}
