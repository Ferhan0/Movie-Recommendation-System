const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const connectDB = require('./config/db');

dotenv.config();
connectDB();

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api/auth', require('./routes/auth'));
app.use('/api/movies', require('./routes/movies'));

app.get('/', (req, res) => {
  res.json({ message: 'API Working' });
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => console.log(`Server on port ${PORT}`));