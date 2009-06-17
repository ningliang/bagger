require File.dirname(__FILE__) + "/../db.rb"

# Function for processing a single file (product)
def process(file) 
  File.open(file, "r") do |fh|
    # Create the new product
    product = Product.create
    
    # Cache photos, purchase points so we don't need a db fetch to check dupes
    product_photos = {}
    product_purchase_points = {}
    
    while (line = fh.gets)
      # Parse object type, fields
      object_name, field_string = line.split(":")
      fields = {}
      field_string.split(",").each do |kv_pair|
        key, value = kv_pair.split("=")
        fields[key] = value
      end
      
      # Names, details, tags, photos, purchase points      
      if object_name == "tag"
        if fields.keys.size == 1
          product.name = fields["name"]
        elsif fields["type"] == "details"
          product.description = fields["name"]
        else 
          tag = Tag.first(:name => fields["name"])
          unless tag
            tag = Tag.create
            tag.name = fields.delete("name")
            tag.type = fields.delete("type")
            tag.meta = fields
            tag.save
          end
          product.tags << tag
        end
      elsif object_name == "photo"
        # Don't take in duplicates (happens with optimized images)
        fields["url"] = fields["url"].split("%3F").first
        unless product_photos.has_key?(fields["url"])
          product.photos << Photo.create(fields)
          product_photos[fields["url"]] = true
        end
     elsif object_name == "purchase_point"
        unless product_purchase_points.has_key?(fields["source"])
          product.purchase_points << PurchasePoint.create(fields)
          product_purchase_points[fields["source"]] = true
        end
      else
        puts "Unknown: #{object_name} #{fields.to_json}"
      end
    end
    
    # Check if duplicates... if so destroy
    if Product.first(:name => product.name) || product.name.nil?
      product.photos.destroy!
      product.purchase_points.destroy!
      product.destroy
    else 
      puts "Saving product #{product.name}"
      product.save
    end
  end
end


# Begin Main Program

# Validate arguments
unless ARGV.length > 0 and File.exists?(ARGV[0])
  puts "Invalid directory"
  exit 1
end
  
# Grab all files from the specified directory and process them
dir = ARGV[0]
Dir.entries(ARGV[0]).each do |file| 
  process("#{dir}/#{file}") unless ["..", ".", ".DS_Store"].include?(file)
end

# Log results to STDOU
puts "#{Product.all.count} products"
puts "#{Photo.all.count} photos"
puts "#{Tag.all.count} tags"
puts "#{PurchasePoint.all.count} purchase points"
  
