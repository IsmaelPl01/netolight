const unpackErrors = (errors) => {
  const unpacked = {};

  errors.forEach((e) => {
    unpacked[e.loc[0]] = e.msg;
  });

  return unpacked;
};

export default unpackErrors;
