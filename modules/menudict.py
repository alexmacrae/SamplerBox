menu = {
    'submenu': {

        0: {
            'name': 'Setlist',
            'submenu': {
                0: {'name': 'Rearrange/Move song', 'fn': ['SelectSong', 'MoveSong']},
                1: {'name': 'Remove missing', 'fn': 'SetlistRemoveMissing'},
                2: {'name': 'Delete songs', 'fn': ['SelectSong', 'DeleteSong']}
            }
        },
        1: {'name': 'Auto chords',
            'submenu':{
                0: {'name':'Chord mode', 'fn': 'ChordMode'},
                1: {'name':'Key', 'fn': 'ChordKey'}
            }
            },
        2: {'name': 'Master volume', 'fn': 'MasterVolumeConfig'},
        3: {'name': 'MIDI Mapping',
            'submenu': {
                0: {
                    'name': 'Note remap',
                    'function_to_map': 'notelist',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                1: {
                    'name': 'Master volume',
                    'function_to_map': 'gv.ac.MasterVolume().setvolume',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        1: {'name': 'Min', 'params': [-70]},
                        2: {'name': 'Max', 'params': [0]},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                2: {
                    'name': 'Reverb',
                    'submenu': {
                        0: {
                            'name': 'Room size',
                            'function_to_map': 'gv.ac.Reverb().setroomsize',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Damping',
                            'function_to_map': 'gv.ac.Reverb().setdamp',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Wet',
                            'function_to_map': 'gv.ac.Reverb().setwet',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Dry',
                            'function_to_map': 'gv.ac.Reverb().setdry',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        4: {
                            'name': 'Width',
                            'function_to_map': 'gv.ac.Reverb().setwidth',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        }
                    }
                },
                3: {
                    'name': 'Voices',
                    'submenu': {
                        0: {
                            'name': 'Voice 1',
                            'function_to_map': 'gv.ac.Voice().voice1',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Voice 2',
                            'function_to_map': 'gv.ac.Voice().voice2',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Voice 3',
                            'function_to_map': 'gv.ac.Voice().voice3',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Voice 4',
                            'function_to_map': 'gv.ac.Voice().voice4',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                    }
                },
                4: {
                    'name': 'Sustain',
                    'function_to_map': 'gv.ac.Sustain().setsustain',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                5: {
                    'name': 'Pitch wheel',
                    'function_to_map': 'gv.ac.PitchWheel().setpitch',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                6: {
                    'name': 'Mod wheel',
                    'function_to_map': 'gv.ac.ModWheel().setmodulation',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                7: {
                    'name': 'SamplerBox Navigation',
                    'submenu': {
                        0: {
                            'name': 'Left',
                            'function_to_map': 'gv.nav.state.left',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Right',
                            'function_to_map': 'gv.nav.state.right',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Enter',
                            'function_to_map': 'gv.nav.state.enter',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Cancel',
                            'function_to_map': 'gv.nav.state.cancel',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        }
                    }
                }
            }
            },
        4: {'name': 'System settings',
            'submenu': {
                0: {'name': 'Max polyphony', 'fn': 'MaxPolyphonyConfig'},
                1: {'name': 'MIDI channel', 'fn': 'MidiChannelConfig'},
                2: {'name': 'Audio channels', 'fn': 'ChannelsConfig'},
                3: {'name': 'Buffer size', 'fn': 'BufferSizeConfig'},
                4: {'name': 'Sample rate', 'fn': 'SampleRateConfig'}

            }

            },
        5: {'name': 'Restart', 'fn': 'gv.sysfunc.restart()'},
        6: {'name': 'Edit definitions', 'fn': ['SelectSong', 'EditDefinition']},
        7: {'name': 'Audio Device', 'fn': 'AudioDevice'}
    }
}
