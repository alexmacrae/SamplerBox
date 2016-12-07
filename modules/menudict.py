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
        1: {'name': 'Edit definitions', 'fn': ['SelectSong', 'EditDefinition']},
        2: {
            'name': 'Auto chords',
            'submenu': {
                0: {'name': 'Chord mode', 'fn': 'ChordMode'},
                1: {'name': 'Key', 'fn': 'ChordKey'}
            }
        },
        3: {'name': 'Master volume', 'fn': 'MasterVolumeConfig'},
        4: {'name': 'MIDI Mapping',
            'submenu': {

                0: {
                    'name': 'Master volume',
                    'function_to_map': 'gv.ac.master_volume.setvolume',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        1: {'name': 'Min', 'params': [-70]},
                        2: {'name': 'Max', 'params': [0]},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                1: {
                    'name': 'Reverb',
                    'submenu': {
                        0: {
                            'name': 'Room size',
                            'function_to_map': 'gv.ac.reverb.setroomsize',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Damping',
                            'function_to_map': 'gv.ac.reverb.setdamp',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Wet',
                            'function_to_map': 'gv.ac.reverb.setwet',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Dry',
                            'function_to_map': 'gv.ac.reverb.setdry',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        4: {
                            'name': 'Width',
                            'function_to_map': 'gv.ac.reverb.setwidth',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        }
                    }
                },
                2: {
                    'name': 'Voices',
                    'submenu': {
                        0: {
                            'name': 'Voice 1',
                            'function_to_map': 'gv.ac.voice.voice1',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Voice 2',
                            'function_to_map': 'gv.ac.voice.voice2',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Voice 3',
                            'function_to_map': 'gv.ac.voice.voice3',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Voice 4',
                            'function_to_map': 'gv.ac.voice.voice4',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                    }
                },
                3: {
                    'name': 'Pitch wheel',
                    'function_to_map': 'gv.ac.pitchbend.set_pitch',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                4: {
                    'name': 'ModWheel:unavail',
                    'function_to_map': 'gv.ac.mod_wheel.set_modulation_disabled',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                5: {
                    'name': 'Sustain',
                    'function_to_map': 'gv.ac.sustain.set_sustain',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                6: {
                    'name': 'System Navigation',
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
        5: {'name': 'System settings',
            'submenu': {
                0: {'name': 'Audio Device', 'fn': 'AudioDevice'},
                1: {'name': 'Max polyphony', 'fn': 'MaxPolyphonyConfig'},
                2: {'name': 'MIDI channel', 'fn': 'MidiChannelConfig'},
                3: {'name': 'Audio channels', 'fn': 'ChannelsConfig'},
                4: {'name': 'Buffer size', 'fn': 'BufferSizeConfig'},
                5: {'name': 'Sample rate', 'fn': 'SampleRateConfig'},
                6: {'name': 'Reverb ON/OFF', 'fn': 'ToggleReverb'}

            }

            },
        # 6: {'name': 'Restart', 'fn': 'gv.sysfunc.restart()'},


    }
}
