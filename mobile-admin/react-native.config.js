module.exports = {
  project: {
    ios: {},
    android: {}, // disable Android platform, other platforms will still autolink
  },
  assets: ['./src/assets/fonts/'],
  dependencies: {
    ...(process.env.NO_FLIPPER ? {'react-native-flipper': {platforms: {ios: null}}} : {}),
  },
};
