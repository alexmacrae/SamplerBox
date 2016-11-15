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
        1: {'name': 'All songs', 'fn': ''},
        2: {'name': 'Master volume', 'fn': 'MasterVolumeConfig'},
        3: {'name': 'MIDI Mapping',
            'submenu': {
                0: {
                    'name': 'Note remap',
                    'functionToMap': 'notelist',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                1: {
                    'name': 'Master volume',
                    'functionToMap': 'ac.MasterVolume.setvolume',
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
                            'functionToMap': 'ac.Reverb.roomsize',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Damping',
                            'functionToMap': 'ac.Reverb.damping',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Wet',
                            'functionToMap': 'ac.Reverb.wet',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Dry',
                            'functionToMap': 'ac.Reverb.dry',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Min', 'params': [0]},
                                2: {'name': 'Max', 'params': [100]},
                                3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        4: {
                            'name': 'Width',
                            'functionToMap': 'ac.Reverb.width',
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
                            'functionToMap': 'ac.Voice.voice1',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Voice 2',
                            'functionToMap': 'ac.Voice.voice2',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Voice 3',
                            'functionToMap': 'ac.Voice.voice3',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Voice 4',
                            'functionToMap': 'ac.Voice.voice4',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                    }
                },
                4: {
                    'name': 'Sustain',
                    'functionToMap': 'ac.Sustain.setsustain',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                5: {
                    'name': 'Pitch wheel',
                    'functionToMap': 'ac.PitchWheel.setpitch',
                    'submenu': {
                        0: {'name': 'Learn', 'fn': 'MidiLearn'},
                        3: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                    }
                },
                6: {
                    'name': 'Mod wheel',
                    'functionToMap': 'ac.ModWheel.setmodulation',
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
                            'functionToMap': 'nav.PresetNav.left',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        1: {
                            'name': 'Right',
                            'functionToMap': 'nav.PresetNav.right',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        2: {
                            'name': 'Enter',
                            'functionToMap': 'nav.PresetNav.enter',
                            'submenu': {
                                0: {'name': 'Learn', 'fn': 'MidiLearn'},
                                1: {'name': 'Delete', 'fn': 'DeleteMidiMap'}
                            }
                        },
                        3: {
                            'name': 'Cancel',
                            'functionToMap': 'nav.PresetNav.cancel',
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

            }
    }
}
